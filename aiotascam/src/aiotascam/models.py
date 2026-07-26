"""Data models for aiotascam."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DiscStatus(StrEnum):
    """Disc/tray status reported by the player (!7?MST)."""

    NO_DISC = "NC"
    DISC_PRESENT = "CI"
    UNFORMATTED = "UF"
    TRAY_OPEN = "TO"
    TRAY_CLOSED = "TC"
    TRAY_ERROR = "TE"


class PlaybackStatus(StrEnum):
    """Playback status reported by the player (!7?SST)."""

    PLAYING = "PL"
    PAUSED = "PP"
    SLOW_REVERSE = "DVSR"
    SLOW_FORWARD = "DVSF"
    SEARCH_REVERSE = "DVFR"
    SEARCH_FORWARD = "DVFF"
    SETUP = "DVSU"
    MEDIA_CENTER = "DVMC"
    TRACK_MENU = "DVTR"
    HOME_MENU = "DVHM"


class CursorDirection(StrEnum):
    """Cursor directions for menu navigation (!7OSDX)."""

    LEFT = "1"
    RIGHT = "2"
    UP = "3"
    DOWN = "4"


@dataclass(slots=True)
class TascamState:
    """Snapshot of the player state."""

    power: bool = False
    disc_status: DiscStatus | None = None
    playback: PlaybackStatus | None = None
    muted: bool | None = None
    elapsed: int | None = None
    remaining: int | None = None
    chapter: int | None = None
    total_chapters: int | None = None
    title: int | None = None
    total_titles: int | None = None

    @property
    def duration(self) -> int | None:
        """Total duration in seconds, if known."""
        if self.elapsed is None or self.remaining is None:
            return None
        return self.elapsed + self.remaining
