"""Coordinator for the Tascam integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiotascam import TascamConnectionError, TascamError, TascamPlayer, TascamState

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

type TascamConfigEntry = ConfigEntry[TascamCoordinator]


class TascamCoordinator(DataUpdateCoordinator[TascamState]):
    """Coordinator that polls the Tascam BD-MP4K player."""

    config_entry: TascamConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: TascamConfigEntry,
        player: TascamPlayer,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.player = player

    async def _async_update_data(self) -> TascamState:
        """Fetch the latest state from the player."""
        try:
            return await self.player.get_state()
        except TascamConnectionError as err:
            raise UpdateFailed(f"Connection to player failed: {err}") from err
        except TascamError as err:
            raise UpdateFailed(f"Error communicating with player: {err}") from err
