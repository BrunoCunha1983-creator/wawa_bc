"""Control buttons for WAHA BC."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import WawaBcEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WAHA BC buttons."""
    runtime = entry.runtime_data
    async_add_entities(
        [
            WawaBcStartButton(runtime.coordinator, entry),
            WawaBcRestartButton(runtime.coordinator, entry),
            WawaBcStopButton(runtime.coordinator, entry),
        ]
    )


class _WawaBcButton(WawaBcEntity, ButtonEntity):
    """Common session button."""

    async def _refresh(self) -> None:
        await self.coordinator.async_request_refresh()


class WawaBcStartButton(_WawaBcButton):
    """Start WAHA session."""

    _attr_name = "Start session"
    _attr_icon = "mdi:play"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_start"

    async def async_press(self) -> None:
        await self.coordinator.api.start_session()
        await self._refresh()


class WawaBcRestartButton(_WawaBcButton):
    """Restart WAHA session."""

    _attr_name = "Restart session"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_restart"

    async def async_press(self) -> None:
        await self.coordinator.api.restart_session()
        await self._refresh()


class WawaBcStopButton(_WawaBcButton):
    """Stop WAHA session without logging out."""

    _attr_name = "Stop session"
    _attr_icon = "mdi:stop"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stop"

    async def async_press(self) -> None:
        await self.coordinator.api.stop_session()
        await self._refresh()
