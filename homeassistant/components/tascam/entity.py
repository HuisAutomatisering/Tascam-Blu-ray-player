"""Base entity for the Tascam integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_BD_MP4K
from .coordinator import TascamCoordinator


class TascamEntity(CoordinatorEntity[TascamCoordinator]):
    """Base class for Tascam entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TascamCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL_BD_MP4K,
            name=f"{MANUFACTURER} {MODEL_BD_MP4K}",
        )
