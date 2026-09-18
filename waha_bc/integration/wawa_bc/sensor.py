"""Sensors for WAHA BC."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import WawaBcEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WAHA BC sensors."""
    runtime = entry.runtime_data
    async_add_entities([WawaBcSessionStatusSensor(runtime.coordinator, entry)])


class WawaBcSessionStatusSensor(WawaBcEntity, SensorEntity):
    """Current WAHA session state."""

    _attr_name = "Session status"
    _attr_icon = "mdi:whatsapp"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_session_status"

    @property
    def native_value(self) -> str | None:
        """Return session status."""
        return self.coordinator.data.get("status")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful non-secret session information."""
        data = self.coordinator.data
        attrs: dict[str, Any] = {
            "session": data.get("name", self.coordinator.api.session_name),
            "engine": data.get("engine"),
        }
        me = data.get("me")
        if isinstance(me, dict):
            attrs["account_id"] = me.get("id")
            attrs["push_name"] = me.get("pushName")
        return attrs
