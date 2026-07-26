"""Async client for the Tascam BD-MP4K Blu-ray player.

Implements the TASCAM BD-MP4K RS-232C/Ethernet protocol over TCP.
The player accepts a single persistent TCP connection on port 9030.
Messages are ``!7`` + command (+ parameters), terminated by CR (0x0D).
The player replies with ``ack``/``nack`` and, for status requests,
an answer message such as ``!7SSTPL``.
"""

from __future__ import annotations

import asyncio
import logging
from enum import Enum
from typing import TypeVar

from .const import (
    ANSWER_TIMEOUT,
    COMMAND_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    END_CHAR,
    START,
)
from .exceptions import (
    TascamCommandError,
    TascamConnectionError,
    TascamTimeoutError,
)
from .models import CursorDirection, DiscStatus, PlaybackStatus, TascamState

_LOGGER = logging.getLogger(__name__)

_ACK = "ack"
_NACK = "nack"


def _parse_time(value: str) -> int | None:
    """Parse an ``hhhmmss`` time string into seconds."""
    if len(value) != 7 or not value.isdigit():
        return None
    hours = int(value[0:3])
    minutes = int(value[3:5])
    seconds = int(value[5:7])
    return hours * 3600 + minutes * 60 + seconds


def _parse_number(value: str) -> int | None:
    """Parse a 4-digit counter value; ``UNKN`` means unknown."""
    if not value.isdigit():
        return None
    return int(value)


class TascamPlayer:
    """Client for a Tascam BD-MP4K Blu-ray player."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._buffer = ""
        self._last_command = 0.0

    @property
    def connected(self) -> bool:
        """Return True if the TCP connection is open."""
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        """Open the TCP connection to the player."""
        if self.connected:
            return
        try:
            async with asyncio.timeout(self.timeout):
                self._reader, self._writer = await asyncio.open_connection(
                    self.host, self.port
                )
        except (OSError, TimeoutError) as err:
            self._reader = None
            self._writer = None
            raise TascamConnectionError(
                f"Cannot connect to {self.host}:{self.port}: {err}"
            ) from err
        self._buffer = ""
        _LOGGER.debug("Connected to %s:%s", self.host, self.port)

    async def disconnect(self) -> None:
        """Close the TCP connection."""
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
        self._reader = None
        self._writer = None
        self._buffer = ""

    async def _write(self, message: str) -> None:
        """Send a raw message, respecting the minimum command interval."""
        if not self.connected:
            await self.connect()
        assert self._writer is not None
        loop = asyncio.get_running_loop()
        elapsed = loop.time() - self._last_command
        if elapsed < COMMAND_INTERVAL:
            await asyncio.sleep(COMMAND_INTERVAL - elapsed)
        _LOGGER.debug("TX: %s", message)
        try:
            self._writer.write(f"{START}{message}{END_CHAR}".encode("latin-1"))
            await self._writer.drain()
        except OSError as err:
            await self.disconnect()
            raise TascamConnectionError(f"Write failed: {err}") from err
        self._last_command = loop.time()

    async def _read_token(self, timeout: float) -> str:
        """Read the next protocol token (ack, nack or a ``!7`` message)."""
        assert self._reader is not None
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            token = self._pop_token()
            if token is not None:
                _LOGGER.debug("RX: %s", token)
                return token
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TascamTimeoutError("Timeout waiting for reply")
            try:
                async with asyncio.timeout(remaining):
                    chunk = await self._reader.read(256)
            except TimeoutError as err:
                raise TascamTimeoutError("Timeout waiting for reply") from err
            except OSError as err:
                await self.disconnect()
                raise TascamConnectionError(f"Read failed: {err}") from err
            if not chunk:
                await self.disconnect()
                raise TascamConnectionError("Connection closed by player")
            self._buffer += chunk.decode("latin-1")

    def _pop_token(self) -> str | None:
        """Extract one complete token from the receive buffer."""
        buffer = self._buffer.lstrip("\r\n ")
        if buffer and not buffer.startswith((_ACK, _NACK, START[0], "n", "a")):
            # Discard unexpected bytes up to the next possible token start.
            starts = [
                index
                for index in (buffer.find(START[0]), buffer.find("a"), buffer.find("n"))
                if index > 0
            ]
            buffer = buffer[min(starts) :] if starts else ""
        if buffer.startswith(_NACK):
            self._buffer = buffer[len(_NACK) :]
            return _NACK
        if buffer.startswith(_ACK):
            self._buffer = buffer[len(_ACK) :]
            return _ACK
        if buffer.startswith(START):
            end = buffer.find(END_CHAR)
            if end == -1:
                self._buffer = buffer
                return None
            self._buffer = buffer[end + 1 :]
            return buffer[:end]
        self._buffer = buffer
        return None

    async def command(self, command: str) -> None:
        """Send a control command and wait for acknowledgement."""
        async with self._lock:
            await self._write(command)
            token = await self._read_token(self.timeout)
            if token == _NACK:
                raise TascamCommandError(f"Player rejected command {command!r}")

    async def request(self, request: str, answer_prefix: str) -> str | None:
        """Send a status request and return the answer payload.

        Returns None when the player sends no matching answer (for
        example ``!7?PWR`` while in standby).
        """
        async with self._lock:
            await self._write(request)
            deadline_timeout = ANSWER_TIMEOUT
            try:
                while True:
                    token = await self._read_token(deadline_timeout)
                    if token == _NACK:
                        raise TascamCommandError(
                            f"Player rejected request {request!r}"
                        )
                    if token.startswith(f"{START}{answer_prefix}"):
                        return token[len(START) + len(answer_prefix) :]
                    # ack or an unrelated notification: keep reading
            except TascamTimeoutError:
                return None

    async def get_power(self) -> bool:
        """Return True when the player is powered on.

        The player only replies to ``!7?PWR`` when it is on; in standby
        the request times out.
        """
        async with self._lock:
            await self._write("?PWR")
            try:
                while True:
                    token = await self._read_token(ANSWER_TIMEOUT)
                    if token in (_ACK, _NACK) or token.startswith(START):
                        return True
            except TascamTimeoutError:
                return False
            except TascamConnectionError:
                return False

    async def get_state(self) -> TascamState:
        """Poll the player and return a full state snapshot."""
        state = TascamState(power=await self.get_power())
        if not state.power:
            return state

        if (value := await self.request("?MST", "MST")) is not None:
            state.disc_status = _lookup_enum(DiscStatus, value)
        if (value := await self.request("?SST", "SST")) is not None:
            state.playback = _lookup_enum(PlaybackStatus, value)
        if (value := await self.request("?MUT", "MUT")) is not None:
            state.muted = value == "00"
        if (value := await self.request("?SET", "SET")) is not None:
            state.elapsed = _parse_time(value)
        if (value := await self.request("?SRT", "SRT")) is not None:
            state.remaining = _parse_time(value)
        if (value := await self.request("?STC", "TNM")) is not None:
            state.chapter = _parse_number(value)
        if (value := await self.request("?STT", "TTN")) is not None:
            state.total_chapters = _parse_number(value)
        if (value := await self.request("?SGN", "GNM")) is not None:
            state.title = _parse_number(value)
        if (value := await self.request("?STG", "TGN")) is not None:
            state.total_titles = _parse_number(value)
        return state

    # Transport controls

    async def play(self) -> None:
        """Start playback."""
        await self.command("PLY")

    async def pause(self) -> None:
        """Pause playback."""
        await self.command("PAS")

    async def stop(self) -> None:
        """Stop playback."""
        await self.command("STP")

    async def next_track(self) -> None:
        """Skip to the next chapter or file."""
        await self.command("SKPNX")

    async def previous_track(self) -> None:
        """Skip to the previous chapter or file."""
        await self.command("SKPPV")

    async def skip_to_chapter(self, chapter: int) -> None:
        """Skip to a specific chapter or file (1-2000)."""
        if not 1 <= chapter <= 2000:
            raise ValueError("Chapter must be between 1 and 2000")
        await self.command(f"SKP{chapter:04d}")

    async def next_title(self) -> None:
        """Skip to the next title or CD track."""
        await self.command("GSKNX")

    async def previous_title(self) -> None:
        """Skip to the previous title or CD track."""
        await self.command("GSKPV")

    # Power and audio

    async def power_off(self) -> None:
        """Switch the player to standby."""
        await self.command("PWR00")

    async def set_mute(self, mute: bool) -> None:
        """Mute (True) or unmute (False) the audio output."""
        await self.command("MUT00" if mute else "MUT01")

    # Tray and menus

    async def open_tray(self) -> None:
        """Open the disc tray."""
        await self.command("OPCOP")

    async def close_tray(self) -> None:
        """Close the disc tray."""
        await self.command("OPCCL")

    async def home(self) -> None:
        """Show the HOME menu."""
        await self.command("HOM")

    async def enter(self) -> None:
        """Confirm the selected menu item."""
        await self.command("ENT")

    async def back(self) -> None:
        """Return to the previous menu screen."""
        await self.command("RET")

    async def top_menu(self) -> None:
        """Show the disc top menu."""
        await self.command("TMN")

    async def popup_menu(self) -> None:
        """Show the disc pop-up menu."""
        await self.command("PMN")

    async def setup_menu(self) -> None:
        """Show the setup menu."""
        await self.command("SMN")

    async def option_menu(self) -> None:
        """Show the option menu."""
        await self.command("OMN")

    async def cursor(self, direction: CursorDirection) -> None:
        """Move the menu cursor."""
        await self.command(f"OSD{direction.value}")


_EnumT = TypeVar("_EnumT", bound=Enum)


def _lookup_enum(enum_cls: type[_EnumT], value: str) -> _EnumT | None:
    """Return the enum member whose value matches, or None."""
    for member in enum_cls:
        if member.value == value:
            return member
    return None
