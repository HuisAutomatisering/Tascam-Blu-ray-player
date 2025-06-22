import socket
import logging
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaType,
)
from homeassistant.const import STATE_PLAYING, STATE_PAUSED, STATE_IDLE, STATE_UNKNOWN

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, COMMANDS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data[CONF_IP_ADDRESS]
    port = config_entry.data[CONF_PORT]
    player = TascamBDMP4KMediaPlayer(ip, port)
    _LOGGER.info("Setting up Tascam BD-MP4K media player entity.")
    async_add_entities([player], update_before_add=True)

class TascamBDMP4KMediaPlayer(MediaPlayerEntity):
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
    )
    _attr_media_content_type = MediaType.VIDEO

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._attr_name = "Tascam BD-MP4K"
        self._attr_unique_id = f"tascam_{ip.replace('.', '_')}_{port}"
        self._attr_state = STATE_IDLE

    def _send_command(self, command):
        try:
            with socket.create_connection((self._ip, self._port), timeout=5) as sock:
                sock.sendall(command.encode())
                response = sock.recv(1024).decode().strip()
                _LOGGER.debug("Sent: %s | Received: %s", command.strip(), response)
                return response
        except Exception as e:
            _LOGGER.error("Tascam command error: %s", e)
            return None

    async def async_update(self):
        # Geen polling implementatie voor nu
        pass

    async def async_media_play(self):
        self._send_command(COMMANDS["play"])
        self._attr_state = STATE_PLAYING
        self.async_write_ha_state()

    async def async_media_pause(self):
        self._send_command(COMMANDS["pause"])
        self._attr_state = STATE_PAUSED
        self.async_write_ha_state()

    async def async_media_next_track(self):
        self._send_command(COMMANDS["next"])

    async def async_media_previous_track(self):
        self._send_command(COMMANDS["previous"])
