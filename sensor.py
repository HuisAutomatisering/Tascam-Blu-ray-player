# TASCAM BD-MP4K Integration - v0.9.3 (2025-06-22)

import logging
import socket
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT

_LOGGER = logging.getLogger(__name__)

QUERIES = {
    "disc_status": "!7?MST",
    "elapsed_time": "!7?SET",
    "remaining_time": "!7?SRT",
    "power_status": "!7?PWR",
    "playback_status": "!7?SST"
}

DISC_STATUS_MAP = {
    "NC": "No disc",
    "CI": "Disc present",
    "UF": "Unformatted",
    "TO": "Tray open",
    "TC": "Tray closed",
    "TE": "Tray error"
}

PLAYBACK_STATUS_MAP = {
    "PL": "Playing",
    "PP": "Paused",
    "DVSR": "Slow Reverse",
    "DVSF": "Slow Forward",
    "DVFR": "Search Reverse",
    "DVFF": "Search Forward",
    "DVSU": "Setup",
    "DVMC": "Media Center",
    "DVTR": "Track Menu",
    "DVHM": "Home Menu"
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data[CONF_IP_ADDRESS]
    port = config_entry.data[CONF_PORT]
    sensors = [TascamStatusSensor(ip, port, key) for key in QUERIES]
    async_add_entities(sensors, update_before_add=True)

class TascamStatusSensor(SensorEntity):
    def __init__(self, ip, port, key):
        self._ip = ip
        self._port = port
        self._key = key
        self._attr_name = f"Tascam {key.replace('_', ' ').title()}"
        self._attr_unique_id = f"tascam_sensor_{key}"
        self.entity_id = f"sensor.tascam_{key}"
        self._attr_native_unit_of_measurement = None
        self._attr_native_value = None

    def _query_status(self, cmd):
        try:
            with socket.create_connection((self._ip, self._port), timeout=5) as sock:
                sock.sendall((cmd + "\r").encode())
                resp = sock.recv(1024).decode().strip()
                _LOGGER.debug("Sent: %s | Received: %s", cmd, resp)
                if "nack" in resp.lower():
                    return None
                return resp
        except Exception as e:
            _LOGGER.error("Sensor query failed: %s", e)
            return None

    def _format_hms(self, hms):
        if len(hms) == 7:
            h = int(hms[0:3])
            m = int(hms[3:5])
            s = int(hms[5:7])
            return f"{h:02}:{m:02}:{s:02}"
        return "00:00:00"

    def _parse_response(self, resp):
        if not resp:
            return None

        if self._key == "disc_status" and "!7MST" in resp:
            code = resp.split("!7MST")[-1].strip()
            return DISC_STATUS_MAP.get(code, code)
        elif self._key == "elapsed_time" and "!7SET" in resp:
            code = resp.split("!7SET")[-1].strip()
            return self._format_hms(code)
        elif self._key == "remaining_time" and "!7SRT" in resp:
            code = resp.split("!7SRT")[-1].strip()
            return self._format_hms(code)
        elif self._key == "power_status":
            return "On" if "ack" in resp.lower() else "Off"
        elif self._key == "playback_status" and "!7SST" in resp:
            code = resp.split("!7SST")[-1].strip()
            return PLAYBACK_STATUS_MAP.get(code, code)

        return None

    async def async_update(self):
        raw = self._query_status(QUERIES[self._key])
        parsed = self._parse_response(raw)
        _LOGGER.debug("Parsed state for %s: %s", self._key, parsed)
        self._attr_native_value = parsed if parsed is not None else "unavailable"
        self.async_write_ha_state()
