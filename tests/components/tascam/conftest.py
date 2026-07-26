"""Fixtures for the Tascam integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

from aiotascam import DiscStatus, PlaybackStatus, TascamState
import pytest

from homeassistant.components.tascam.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT

from tests.common import MockConfigEntry


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.tascam.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_player() -> Generator[MagicMock]:
    """Mock a Tascam player client."""
    with (
        patch(
            "homeassistant.components.tascam.TascamPlayer", autospec=True
        ) as player_mock,
        patch(
            "homeassistant.components.tascam.config_flow.TascamPlayer",
            new=player_mock,
        ),
    ):
        player = player_mock.return_value
        player.get_state.return_value = TascamState(
            power=True,
            disc_status=DiscStatus.DISC_PRESENT,
            playback=PlaybackStatus.PLAYING,
            muted=False,
            elapsed=65,
            remaining=35,
            chapter=1,
            total_chapters=12,
            title=1,
            total_titles=1,
        )
        yield player


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Tascam BD-MP4K",
        data={CONF_HOST: "192.168.1.50", CONF_PORT: 9030},
    )
