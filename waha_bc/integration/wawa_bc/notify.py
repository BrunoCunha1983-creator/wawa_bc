"""Notification entity for WAHA BC."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_RECIPIENT
from .entity import WawaBcEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the WhatsApp notification entity."""
    runtime = entry.runtime_data
    async_add_entities(
        [
            WawaBcNotifyEntity(
                runtime.coordinator,
                entry,
                entry.data[CONF_RECIPIENT],
            )
        ]
    )


class WawaBcNotifyEntity(WawaBcEntity, NotifyEntity):
    """Send Home Assistant notifications through WhatsApp."""

    _attr_name = "WhatsApp BC"
    _attr_icon = "mdi:whatsapp"
    _attr_has_entity_name = False
    _attr_supported_features = NotifyEntityFeature.TITLE

    def __init__(self, coordinator, entry: ConfigEntry, recipient: str) -> None:
        super().__init__(coordinator, entry)
        self._recipient = recipient
        self._attr_unique_id = f"{entry.entry_id}_notify"

    async def async_send_message(
        self, message: str, title: str | None = None
    ) -> None:
        """Send the message to the configured default recipient."""
        text = f"*{title}*\n{message}" if title else message
        await self.coordinator.api.send_text(self._recipient, text)
