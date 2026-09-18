"""Small asynchronous WAHA API client used by WAHA BC."""

from __future__ import annotations

import re
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout


class WahaApiError(Exception):
    """Base WAHA API error."""


class WahaAuthError(WahaApiError):
    """Authentication failed."""


class WahaNotFoundError(WahaApiError):
    """Requested WAHA resource does not exist."""


class WahaConnectionError(WahaApiError):
    """WAHA could not be reached."""


class WahaApi:
    """Asynchronous client for the WAHA HTTP API."""

    def __init__(
        self,
        client: ClientSession,
        base_url: str,
        api_key: str,
        session_name: str,
        verify_ssl: bool = False,
    ) -> None:
        self._client = client
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session_name = session_name
        self.verify_ssl = verify_ssl

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "headers": self.headers,
            "timeout": ClientTimeout(total=15),
        }
        if json is not None:
            kwargs["json"] = json
        if self.base_url.startswith("https://") and not self.verify_ssl:
            kwargs["ssl"] = False

        try:
            async with self._client.request(
                method, f"{self.base_url}{path}", **kwargs
            ) as response:
                if response.status in (401, 403):
                    raise WahaAuthError("WAHA rejected the API key")
                if response.status == 404:
                    raise WahaNotFoundError(await response.text())
                if response.status >= 400:
                    body = await response.text()
                    raise WahaApiError(
                        f"WAHA HTTP {response.status}: {body[:500]}"
                    )
                if response.status == 204:
                    return None
                try:
                    return await response.json(content_type=None)
                except ValueError:
                    return await response.text()
        except (WahaApiError, WahaAuthError, WahaNotFoundError):
            raise
        except (ClientError, TimeoutError) as err:
            raise WahaConnectionError(str(err)) from err

    async def get_session(self) -> dict[str, Any]:
        data = await self._request(
            "GET", f"/api/sessions/{self.session_name}"
        )
        if not isinstance(data, dict):
            raise WahaApiError("WAHA returned an invalid session response")
        return data

    async def send_text(self, target: str, message: str) -> Any:
        return await self._request(
            "POST",
            "/api/sendText",
            json={
                "session": self.session_name,
                "chatId": normalize_chat_id(target),
                "text": message,
            },
        )

    async def start_session(self) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/sessions/{self.session_name}/start"
        )

    async def stop_session(self) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/sessions/{self.session_name}/stop"
        )

    async def restart_session(self) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/sessions/{self.session_name}/restart"
        )


def normalize_chat_id(target: str) -> str:
    """Convert a telephone number to the WAHA chat id format.

    Existing WAHA ids such as 12345@g.us or 3519...@c.us are preserved.
    """
    target = str(target).strip()
    if "@" in target:
        return target

    digits = re.sub(r"\D", "", target)
    if not digits:
        raise WahaApiError("Invalid WhatsApp target")
    return f"{digits}@c.us"
