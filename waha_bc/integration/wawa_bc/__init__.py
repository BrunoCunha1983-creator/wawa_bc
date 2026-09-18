"""WAHA BC integration for Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WahaApi, WahaApiError
from .const import (
    CONF_API_KEY,
    CONF_RECIPIENT,
    CONF_SESSION,
    CONF_VERIFY_SSL,
    DEFAULT_WEBHOOK_ID,
    DOMAIN,
    EVENT_MESSAGE_RECEIVED,
    EVENT_MESSAGE_SENT,
    EVENT_REACTION_RECEIVED,
    EVENT_SESSION_STATUS,
    NOTIFY_SERVICE,
    SERVICE_SEND_MESSAGE,
    WEBHOOK_HEADER,
)
from .coordinator import WawaBcCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.NOTIFY,
]

TARGET_SCHEMA = vol.Any(cv.string, [cv.string])
SEND_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("title"): cv.string,
        vol.Optional("target"): TARGET_SCHEMA,
    }
)


@dataclass
class WawaBcRuntimeData:
    """Runtime data shared by WAHA BC platforms."""

    api: WahaApi
    coordinator: WawaBcCoordinator
    default_recipient: str


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up WAHA BC from the UI."""
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, False)
    client = async_get_clientsession(hass, verify_ssl)
    api = WahaApi(
        client,
        entry.data[CONF_URL],
        entry.data[CONF_API_KEY],
        entry.data[CONF_SESSION],
        verify_ssl,
    )
    coordinator = WawaBcCoordinator(hass, entry, api)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(str(err)) from err

    runtime = WawaBcRuntimeData(
        api=api,
        coordinator=coordinator,
        default_recipient=entry.data[CONF_RECIPIENT],
    )
    entry.runtime_data = runtime

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["entry"] = entry
    hass.data[DOMAIN]["runtime"] = runtime

    if not hass.data[DOMAIN].get("webhook_registered"):
        webhook.async_register(
            hass,
            DOMAIN,
            "WAHA BC incoming events",
            DEFAULT_WEBHOOK_ID,
            _handle_webhook,
        )
        hass.data[DOMAIN]["webhook_registered"] = True

    _register_services(hass, runtime)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload WAHA BC."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if not unload_ok:
        return False

    if hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)

    if hass.data.get(DOMAIN, {}).get("legacy_notify_registered"):
        if hass.services.has_service("notify", NOTIFY_SERVICE):
            hass.services.async_remove("notify", NOTIFY_SERVICE)

    if hass.data.get(DOMAIN, {}).get("webhook_registered"):
        webhook.async_unregister(hass, DEFAULT_WEBHOOK_ID)

    hass.data.pop(DOMAIN, None)
    return True


def _register_services(
    hass: HomeAssistant, runtime: WawaBcRuntimeData
) -> None:
    """Register native and compatibility send services."""

    async def handle_send_message(call: ServiceCall) -> None:
        await _send_from_call(hass, runtime, call)

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_MESSAGE,
            handle_send_message,
            schema=SEND_MESSAGE_SCHEMA,
        )

    if not hass.services.has_service("notify", NOTIFY_SERVICE):
        hass.services.async_register(
            "notify",
            NOTIFY_SERVICE,
            handle_send_message,
            schema=SEND_MESSAGE_SCHEMA,
        )
        hass.data[DOMAIN]["legacy_notify_registered"] = True


async def _send_from_call(
    hass: HomeAssistant,
    runtime: WawaBcRuntimeData,
    call: ServiceCall,
) -> None:
    """Send one Home Assistant service call through WhatsApp."""
    targets = call.data.get("target", runtime.default_recipient)
    if isinstance(targets, str):
        targets = [targets]

    message = call.data["message"]
    if title := call.data.get("title"):
        message = f"*{title}*\n{message}"

    try:
        for target in targets:
            await runtime.api.send_text(target, message)
            hass.bus.async_fire(
                EVENT_MESSAGE_SENT,
                {
                    "target": target,
                    "session": runtime.api.session_name,
                    "message": message,
                },
            )
    except WahaApiError as err:
        raise HomeAssistantError(
            f"WAHA BC failed to send the WhatsApp message: {err}"
        ) from err


async def _handle_webhook(
    hass: HomeAssistant,
    webhook_id: str,
    request: web.Request,
) -> web.Response:
    """Receive WAHA webhooks and expose them as Home Assistant events."""
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return web.json_response(
            {"ok": False, "error": "integration_not_loaded"},
            status=503,
        )

    entry: ConfigEntry = domain_data["entry"]
    runtime: WawaBcRuntimeData = domain_data["runtime"]

    expected = hashlib.sha256(
        entry.data[CONF_API_KEY].encode("utf-8")
    ).hexdigest()
    supplied = request.headers.get(WEBHOOK_HEADER, "")
    if not hmac.compare_digest(expected, supplied):
        return web.json_response(
            {"ok": False, "error": "unauthorized"},
            status=401,
        )

    try:
        data: dict[str, Any] = await request.json()
    except ValueError:
        return web.json_response(
            {"ok": False, "error": "invalid_json"},
            status=400,
        )

    event_name = data.get("event")
    payload = data.get("payload") or {}

    if event_name == "message":
        event_data = {
            "session": data.get("session"),
            "engine": data.get("engine"),
            "id": data.get("id"),
            "timestamp": data.get("timestamp"),
            "from": payload.get("from"),
            "to": payload.get("to"),
            "body": payload.get("body"),
            "from_me": payload.get("fromMe"),
            "has_media": payload.get("hasMedia"),
            "payload": payload,
        }
        hass.bus.async_fire(EVENT_MESSAGE_RECEIVED, event_data)

    elif event_name == "session.status":
        status = payload.get("status")
        hass.bus.async_fire(
            EVENT_SESSION_STATUS,
            {
                "session": data.get("session"),
                "status": status,
                "payload": payload,
            },
        )
        current = dict(runtime.coordinator.data or {})
        if status is not None:
            current["status"] = status
        runtime.coordinator.async_set_updated_data(current)

    elif event_name == "message.reaction":
        hass.bus.async_fire(
            EVENT_REACTION_RECEIVED,
            {
                "session": data.get("session"),
                "payload": payload,
            },
        )

    return web.json_response({"ok": True})
