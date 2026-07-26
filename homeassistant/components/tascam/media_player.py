"""Media player platform for the Tascam integration."""

from __future__ import annotations

from aiotascam import DiscStatus, PlaybackStatus

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import TascamConfigEntry, TascamCoordinator
from .entity import TascamEntity

PARALLEL_UPDATES = 1

_PLAYING_STATUSES = {
    PlaybackStatus.PLAYING,
    PlaybackStatus.SLOW_FORWARD,
    PlaybackStatus.SLOW_REVERSE,
    PlaybackStatus.SEARCH_FORWARD,
    PlaybackStatus.SEARCH_REVERSE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TascamConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Tascam media player."""
    async_add_entities([TascamMediaPlayer(entry.runtime_data)])


class TascamMediaPlayer(TascamEntity, MediaPlayerEntity):
    """Representation of the Tascam BD-MP4K Blu-ray player."""

    _attr_name = None
    _attr_media_content_type = MediaType.VIDEO
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(self, coordinator: TascamCoordinator) -> None:
        """Initialize the media player."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        data = self.coordinator.data
        if not data.power:
            return MediaPlayerState.OFF
        if data.playback in _PLAYING_STATUSES:
            return MediaPlayerState.PLAYING
        if data.playback is PlaybackStatus.PAUSED:
            return MediaPlayerState.PAUSED
        return MediaPlayerState.IDLE

    @property
    def is_volume_muted(self) -> bool | None:
        """Return True if the player is muted."""
        return self.coordinator.data.muted

    @property
    def media_position(self) -> int | None:
        """Return the current playback position in seconds."""
        return self.coordinator.data.elapsed

    @property
    def media_position_updated_at(self):
        """Return when the position was last updated."""
        if self.coordinator.data.elapsed is None:
            return None
        return dt_util.utcnow()

    @property
    def media_duration(self) -> int | None:
        """Return the duration of the current media in seconds."""
        return self.coordinator.data.duration

    @property
    def media_track(self) -> int | None:
        """Return the current chapter or file number."""
        return self.coordinator.data.chapter

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Return additional state attributes."""
        data = self.coordinator.data
        return {
            "disc_status": data.disc_status.name.lower() if data.disc_status else None,
            "title": data.title,
            "total_titles": data.total_titles,
            "total_chapters": data.total_chapters,
        }

    async def async_media_play(self) -> None:
        """Start playback."""
        await self.coordinator.player.play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Pause playback."""
        await self.coordinator.player.pause()
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Stop playback."""
        await self.coordinator.player.stop()
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Skip to the next chapter or file."""
        await self.coordinator.player.next_track()
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Skip to the previous chapter or file."""
        await self.coordinator.player.previous_track()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the player off (standby)."""
        await self.coordinator.player.power_off()
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the player."""
        await self.coordinator.player.set_mute(mute)
        await self.coordinator.async_request_refresh()
