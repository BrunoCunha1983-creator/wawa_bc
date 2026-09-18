"""Base entities for WAHA BC."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WawaBcCoordinator


class WawaBcEntity(CoordinatorEntity[WawaBcCoordinator]):
    """Common WAHA BC entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WawaBcCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="WAHA BC",
            manufacturer="WAHA / WAHA BC",
            model="WhatsApp HTTP API",
            configuration_url=coordinator.api.base_url,
        )
