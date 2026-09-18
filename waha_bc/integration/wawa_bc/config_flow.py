"""Config flow for WAHA BC."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from yarl import URL

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    WahaApi,
    WahaApiError,
    WahaAuthError,
    WahaConnectionError,
    WahaNotFoundError,
)
from .const import (
    CONF_API_KEY,
    CONF_RECIPIENT,
    CONF_SESSION,
    CONF_VERIFY_SSL,
    DEFAULT_PORT,
    DEFAULT_SESSION,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class WawaBcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure WAHA BC."""

    VERSION = 1

    def _default_url(self) -> str:
        try:
            current = URL(
                get_url(
                    self.hass,
                    prefer_external=False,
                    allow_cloud=False,
                )
            )
            current = current.with_scheme("http").with_port(DEFAULT_PORT)
            return str(current.with_path("").with_query(None).with_fragment(None)).rstrip("/")
        except (NoURLAvailableError, ValueError):
            return f"http://homeassistant.local:{DEFAULT_PORT}"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle user setup."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            client = async_get_clientsession(
                self.hass, user_input[CONF_VERIFY_SSL]
            )
            api = WahaApi(
                client,
                user_input[CONF_URL],
                user_input[CONF_API_KEY],
                user_input[CONF_SESSION],
                user_input[CONF_VERIFY_SSL],
            )
            try:
                await api.get_session()
            except WahaAuthError:
                errors["base"] = "invalid_auth"
            except WahaNotFoundError:
                errors["base"] = "session_not_found"
            except WahaConnectionError:
                errors["base"] = "cannot_connect"
            except WahaApiError:
                _LOGGER.exception("WAHA API setup error")
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected WAHA BC setup error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_URL].rstrip('/')}::{user_input[CONF_SESSION]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"WAHA BC ({user_input[CONF_SESSION]})",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_URL,
                    default=(user_input or {}).get(
                        CONF_URL, self._default_url()
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.URL)
                ),
                vol.Required(CONF_API_KEY): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Required(
                    CONF_SESSION,
                    default=(user_input or {}).get(
                        CONF_SESSION, DEFAULT_SESSION
                    ),
                ): str,
                vol.Required(CONF_RECIPIENT): str,
                vol.Required(
                    CONF_VERIFY_SSL,
                    default=(user_input or {}).get(
                        CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
                    ),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
