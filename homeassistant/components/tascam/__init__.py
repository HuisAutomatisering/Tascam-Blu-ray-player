"""The Tascam integration."""

from __future__ import annotations

from aiotascam import TascamConnectionError, TascamPlayer

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import TascamConfigEntry, TascamCoordinator

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: TascamConfigEntry) -> bool:
    """Set up Tascam from a config entry."""
    player = TascamPlayer(entry.data[CONF_HOST], entry.data[CONF_PORT])
    try:
        await player.connect()
    except TascamConnectionError as err:
        raise ConfigEntryNotReady(
            f"Cannot connect to {entry.data[CONF_HOST]}"
        ) from err

    coordinator = TascamCoordinator(hass, entry, player)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TascamConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.player.disconnect()
    return unload_ok
