"""Exceptions for aiotascam."""

from __future__ import annotations


class TascamError(Exception):
    """Base exception for aiotascam."""


class TascamConnectionError(TascamError):
    """Raised when the connection to the player fails."""


class TascamCommandError(TascamError):
    """Raised when the player rejects a command (NACK) or does not reply."""


class TascamTimeoutError(TascamConnectionError):
    """Raised when the player does not reply in time."""
