"""
TASCAM BD-MP4K Media Player Integration for Home Assistant
"""
import asyncio
import logging
import socket

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.const import (
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
)
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'tascam_bd_mp4k'

CONF_HOST = 'host'
CONF_PORT = 'port'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=9030): cv.port
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the TASCAM media player platform."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    # Create TASCAM media player instance
    player = TascamMediaPlayer(host, port)

    # Add the media player entity
    async_add_entities([player])

class TascamMediaPlayer(MediaPlayerEntity):
    """Representation of a TASCAM media player."""

    def __init__(self, host, port):
        """Initialize the TASCAM media player."""
        self._host = host
        self._port = port
        self._state = STATE_OFF
        self._name = "TASCAM Media Player"
        self._socket = None

    async def async_update(self):
        """Update the state of the media player."""
        # Implement update logic here if needed
        pass

    async def async_turn_on(self):
        """Turn on the media player."""
        await self._send_command("!7PWR01")
        self._state = STATE_IDLE

    async def async_turn_off(self):
        """Turn off the media player."""
        await self._send_command("!7PWR00")
        self._state = STATE_OFF

    async def async_media_play(self):
        """Send play command."""
        await self._send_command("!7PLY")
        self._state = STATE_PLAYING

    async def async_media_pause(self):
        """Send pause command."""
        await self._send_command("!7PAS")
        self._state = STATE_PAUSED

    async def _send_command(self, command):
        """Send command to the TASCAM media player."""
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            await self._socket.connect((self._host, self._port))

        try:
            await self.hass.async_add_executor_job(self._socket.send, command.encode())
        except (ConnectionError, OSError) as err:
            _LOGGER.error("Error communicating with TASCAM media player: %s", err)
            self._socket = None
            raise

    @property
    def name(self):
        """Return the name of the media player."""
        return self._name

    @property
    def state(self):
        """Return the state of the media player."""
        return self._state

    @property
    def available(self):
        """Return True if the media player is available."""
        return self._socket is not None
