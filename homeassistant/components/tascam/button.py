"""Button platform for the Tascam integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from aiotascam import CursorDirection, TascamPlayer

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import TascamConfigEntry, TascamCoordinator
from .entity import TascamEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class TascamButtonEntityDescription(ButtonEntityDescription):
    """Description of a Tascam button."""

    press_fn: Callable[[TascamPlayer], Coroutine[Any, Any, None]]


BUTTONS: tuple[TascamButtonEntityDescription, ...] = (
    TascamButtonEntityDescription(
        key="open_tray",
        translation_key="open_tray",
        press_fn=lambda player: player.open_tray(),
    ),
    TascamButtonEntityDescription(
        key="close_tray",
        translation_key="close_tray",
        press_fn=lambda player: player.close_tray(),
    ),
    TascamButtonEntityDescription(
        key="home",
        translation_key="home",
        press_fn=lambda player: player.home(),
    ),
    TascamButtonEntityDescription(
        key="enter",
        translation_key="enter",
        press_fn=lambda player: player.enter(),
    ),
    TascamButtonEntityDescription(
        key="back",
        translation_key="back",
        press_fn=lambda player: player.back(),
    ),
    TascamButtonEntityDescription(
        key="top_menu",
        translation_key="top_menu",
        press_fn=lambda player: player.top_menu(),
    ),
    TascamButtonEntityDescription(
        key="popup_menu",
        translation_key="popup_menu",
        press_fn=lambda player: player.popup_menu(),
    ),
    TascamButtonEntityDescription(
        key="option_menu",
        translation_key="option_menu",
        press_fn=lambda player: player.option_menu(),
    ),
    TascamButtonEntityDescription(
        key="cursor_up",
        translation_key="cursor_up",
        press_fn=lambda player: player.cursor(CursorDirection.UP),
    ),
    TascamButtonEntityDescription(
        key="cursor_down",
        translation_key="cursor_down",
        press_fn=lambda player: player.cursor(CursorDirection.DOWN),
    ),
    TascamButtonEntityDescription(
        key="cursor_left",
        translation_key="cursor_left",
        press_fn=lambda player: player.cursor(CursorDirection.LEFT),
    ),
    TascamButtonEntityDescription(
        key="cursor_right",
        translation_key="cursor_right",
        press_fn=lambda player: player.cursor(CursorDirection.RIGHT),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TascamConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Tascam buttons."""
    coordinator = entry.runtime_data
    async_add_entities(
        TascamButton(coordinator, description) for description in BUTTONS
    )


class TascamButton(TascamEntity, ButtonEntity):
    """A menu/tray control button for the Tascam BD-MP4K."""

    entity_description: TascamButtonEntityDescription

    def __init__(
        self,
        coordinator: TascamCoordinator,
        description: TascamButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{description.key}"
        )

    async def async_press(self) -> None:
        """Send the command to the player."""
        await self.entity_description.press_fn(self.coordinator.player)
