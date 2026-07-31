"""Async TCP protocol client for the Tascam BD-MP4K.

The BD-MP4K protocol specification requires that the TCP connection is held
open continuously and that only one client connects at a time. Therefore this
integration maintains a single shared connection for all entities.

Protocol notes (RS-232C/Ethernet spec v1.01):
- Commands are ASCII, start with ``!7`` and end with CR (0x0D).
- The device replies ``ack`` (optionally followed by ``+`` and an answer such
  as ``!7SET0011230``) or ``nack``.
- The interval between commands must be at least 30 ms.
- The device may push unsolicited status notifications at any time; the
  controller should reply with ``ack``.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)

START = "!7"
CR = "\r"
ACK = "ack"
NACK = "nack"

COMMAND_INTERVAL = 0.03  # 30 ms minimum between commands (spec 4.3.6)
RESPONSE_TIMEOUT = 1.0
CONNECT_TIMEOUT = 5.0

_MESSAGE_RE = re.compile(r"(!7[A-Z0-9]{3}[^!]*|ack|nack)")


class TascamError(Exception):
    """Base error for Tascam protocol failures."""


class TascamConnectionError(TascamError):
    """Raised when the device cannot be reached."""


class TascamNackError(TascamError):
    """Raised when the device replies with NACK."""


class TascamClient:
    """Maintain a single persistent connection to the BD-MP4K."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._last_command = 0.0
        self._notification_callback: Callable[[str], None] | None = None

    @property
    def connected(self) -> bool:
        """Return True if the connection is open."""
        return self._writer is not None and not self._writer.is_closing()

    def set_notification_callback(
        self, callback: Callable[[str], None] | None
    ) -> None:
        """Register a callback for unsolicited status notifications."""
        self._notification_callback = callback

    async def async_connect(self) -> None:
        """Open the TCP connection."""
        if self.connected:
            return
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, TimeoutError) as err:
            self._reader = None
            self._writer = None
            raise TascamConnectionError(
                f"Cannot connect to {self._host}:{self._port}: {err}"
            ) from err
        _LOGGER.debug("Connected to %s:%s", self._host, self._port)

    async def async_disconnect(self) -> None:
        """Close the TCP connection."""
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
        self._reader = None
        self._writer = None

    async def async_send(self, command: str) -> str | None:
        """Send a command and return the answer message, if any.

        Returns the ``!7XXX...`` answer for status requests, or None for
        plain control commands that are only acknowledged.
        Raises TascamNackError on NACK and TascamConnectionError on I/O
        failure.
        """
        async with self._lock:
            await self.async_connect()
            await self._respect_interval()
            assert self._writer is not None and self._reader is not None
            try:
                self._writer.write(f"{command}{CR}".encode("ascii"))
                await self._writer.drain()
                self._last_command = time.monotonic()
                return await self._read_response(command)
            except (OSError, TimeoutError) as err:
                await self.async_disconnect()
                raise TascamConnectionError(
                    f"I/O error for command {command}: {err}"
                ) from err

    async def _respect_interval(self) -> None:
        """Enforce the 30 ms minimum interval between commands."""
        elapsed = time.monotonic() - self._last_command
        if elapsed < COMMAND_INTERVAL:
            await asyncio.sleep(COMMAND_INTERVAL - elapsed)

    async def _read_response(self, command: str) -> str | None:
        """Read until an ack/nack (and optional answer) is received."""
        assert self._reader is not None
        buffer = ""
        acked = False
        answer: str | None = None
        deadline = time.monotonic() + RESPONSE_TIMEOUT
        while time.monotonic() < deadline:
            timeout = max(deadline - time.monotonic(), 0.01)
            try:
                chunk = await asyncio.wait_for(
                    self._reader.read(256), timeout=timeout
                )
            except TimeoutError:
                break
            if not chunk:
                await self.async_disconnect()
                raise TascamConnectionError("Connection closed by device")
            buffer += chunk.decode("ascii", errors="replace")
            acked, answer, done, notified = self._parse_buffer(
                command, buffer, acked
            )
            if notified:
                # Spec 4.4.3: the controller must ack status notifications,
                # otherwise the device resends them.
                self._writer.write(f"{ACK}{CR}".encode("ascii"))
                await self._writer.drain()
            if done:
                return answer
        if acked:
            # Control command: ack without answer is a valid, complete reply.
            return answer
        await self.async_disconnect()
        raise TascamConnectionError(f"No reply to {command}")

    def _parse_buffer(
        self, command: str, buffer: str, acked: bool
    ) -> tuple[bool, str | None, bool, bool]:
        """Parse tokens from the receive buffer.

        Returns (acked, answer, done, notified). Unsolicited notifications
        are passed to the notification callback.
        """
        answer: str | None = None
        notified = False
        is_request = command.startswith(f"{START}?")
        for token in _MESSAGE_RE.findall(buffer):
            token = token.strip("\r\n+ ")
            if not token:
                continue
            if token == NACK:
                raise TascamNackError(f"Device replied NACK to {command}")
            if token == ACK:
                acked = True
                if not is_request:
                    return acked, None, True, notified
                continue
            if token.startswith(START):
                if acked and is_request and answer is None:
                    answer = token
                    return acked, answer, True, notified
                # Unsolicited status notification.
                notified = True
                if self._notification_callback is not None:
                    self._notification_callback(token)
        return acked, answer, False, notified
