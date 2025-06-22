# TASCAM BD-MP4K Integration - v0.9.3 (2025-06-22)

import logging
import socket
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT

_LOGGER = logging.getLogger(__name__)

COMMANDS = {
    "tray_open": "!7OPCOP",
    "tray_close": "!7OPCCL",
    "stop": "!7STP",
    "enter": "!7ENT",
    "home": "!7HOM",
    "mute_on": "!7MUT00",
    "mute_off": "!7MUT01",
    "power_off": "!7PWR00",
    "power_on": "!7PWR01",
    "title_menu": "!7TMN",
    "return": "!7RET"
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data[CONF_IP_ADDRESS]
    port = config_entry.data[CONF_PORT]
    entities = [TascamButton(ip, port, name, cmd) for name, cmd in COMMANDS.items()]
    async_add_entities(entities)

class TascamButton(ButtonEntity):
    def __init__(self, ip, port, name, cmd):
        self._ip = ip
        self._port = port
        self._cmd = cmd
        self._attr_name = f"Tascam {name.replace('_', ' ').title()}"
        self._attr_unique_id = f"tascam_button_{name}"

    def press(self) -> None:
        try:
            with socket.create_connection((self._ip, self._port), timeout=5) as sock:
                sock.sendall((self._cmd + "\r").encode())
                resp = sock.recv(1024).decode().strip()
                _LOGGER.debug("Sent: %s | Received: %s", self._cmd, resp)
        except Exception as e:
            _LOGGER.error("Failed to send command %s: %s", self._cmd, e)
