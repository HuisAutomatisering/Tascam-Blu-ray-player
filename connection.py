import asyncio
import socket
import logging

_LOGGER = logging.getLogger(__name__)

class TascamConnection:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._reader = None
        self._writer = None
        self._lock = asyncio.Lock()

    async def connect(self):
        try:
            _LOGGER.debug("Connecting to Tascam BD-MP4K at %s:%s", self._ip, self._port)
            self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)
        except Exception as e:
            _LOGGER.error("Failed to connect to Tascam: %s", e)
            self._reader = None
            self._writer = None

    async def disconnect(self):
        if self._writer:
            _LOGGER.debug("Disconnecting from Tascam BD-MP4K")
            self._writer.close()
            await self._writer.wait_closed()
            self._reader = None
            self._writer = None

    async def send_command(self, command: str):
        async with self._lock:
            if not self._writer:
                await self.connect()
            if not self._writer:
                return None
            try:
                _LOGGER.debug("Sending command: %s", command.strip())
                self._writer.write(command.encode())
                await self._writer.drain()
                response = await asyncio.wait_for(self._reader.read(1024), timeout=1.0)
                response_decoded = response.decode().strip()
                _LOGGER.debug("Received response: %s", response_decoded)
                return response_decoded
            except Exception as e:
                _LOGGER.error("Error sending command to Tascam: %s", e)
                await self.disconnect()
                return None
