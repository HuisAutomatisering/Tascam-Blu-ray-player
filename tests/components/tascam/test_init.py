"""Tests for the Tascam integration setup."""

from __future__ import annotations

from unittest.mock import MagicMock

from aiotascam import TascamConnectionError

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_load_unload_entry(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test loading and unloading a config entry."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    mock_player.disconnect.assert_called()


async def test_setup_entry_cannot_connect(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the entry is set to retry when the player is unreachable."""
    mock_player.connect.side_effect = TascamConnectionError("boom")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
