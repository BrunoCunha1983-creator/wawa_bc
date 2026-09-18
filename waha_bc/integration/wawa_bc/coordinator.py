"""WAHA BC data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WahaApi, WahaApiError

_LOGGER = logging.getLogger(__name__)


class WawaBcCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the configured WAHA session."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: WahaApi,
    ) -> None:
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="WAHA BC",
            update_interval=timedelta(seconds=20),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_session()
        except WahaApiError as err:
            raise UpdateFailed(str(err)) from err
