"""Tests for the Tascam config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from aiotascam import TascamConnectionError

from homeassistant.components.tascam.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

USER_INPUT = {CONF_HOST: "192.168.1.50", CONF_PORT: 9030}


async def test_full_user_flow(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the full happy path of the user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tascam BD-MP4K"
    assert result["data"] == USER_INPUT
    assert len(mock_setup_entry.mock_calls) == 1


async def test_cannot_connect(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the flow recovers from a connection error."""
    mock_player.connect.side_effect = TascamConnectionError("boom")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    mock_player.connect.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_unknown_error(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the flow recovers from an unexpected error."""
    mock_player.connect.side_effect = ValueError("boom")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}

    mock_player.connect.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_duplicate_host_aborts(
    hass: HomeAssistant,
    mock_player: MagicMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that a host can only be configured once."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
