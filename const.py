DOMAIN = "tascam_bdmp4k"
DEFAULT_PORT = 9030
DEFAULT_NAME = "Tascam BD-MP4K"
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"

ATTR_TRACK_NUMBER = "track_number"
ATTR_TIME_CODE = "time_code"

COMMANDS = {
    "play": "!7PLY\r",
    "pause": "!7PAS\r",
    "stop": "!7STP\r",
    "next": "!7SKPNX\r",
    "previous": "!7SKPPV\r",
    "fast_forward": "!7SCNFF\r",
    "rewind": "!7SCNRF\r",
    "tray_open": "!7OPCOP\r",
    "tray_close": "!7OPCCL\r",
    "status": "!7?SST\r",
    "track_number": "!7?TNM\r",
    "time_code": "!7?SET\r"
}

STATE_MAP = {
    "PL": "playing",
    "PP": "paused",
    "ST": "stopped",
    "DVTR": "playing",
    "SSTDVSX": "slow_play",
    "SSTDVFX": "fast_forward",
    "SSTDVSU": "setup",
    "SSTDVMC": "media_mode",
    "SSTDVHM": "home_menu",
}
