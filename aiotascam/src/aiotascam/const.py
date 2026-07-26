"""Constants for aiotascam."""

from __future__ import annotations

DEFAULT_PORT = 9030
DEFAULT_TIMEOUT = 5.0

# Protocol framing
START = "!7"
END_CHAR = "\r"

# The spec requires at least 30 ms between commands.
COMMAND_INTERVAL = 0.05
# How long to wait for an answer to a status request. The player replies
# within 30 ms over IP; standby is detected by the absence of a reply.
ANSWER_TIMEOUT = 1.0
