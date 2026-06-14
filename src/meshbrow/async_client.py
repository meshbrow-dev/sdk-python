"""Async Meshbrow API client."""

from __future__ import annotations

from typing import Any

import httpx

from meshbrow.types import Fleet, Screenshot, Session, SessionList


class AsyncMeshbrow:
    """Async client for the Meshbrow API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.meshbrow.dev",
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "meshbrow-python/0.1.0",
            },
            timeout=timeout,
        )

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        resp = await self._client.request(method, path, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204:
            return None
        body = resp.json()
        return body.get("data", body)

    # --- Sessions ---

    async def create_session(
        self,
        *,
        stealth: str = "max",
        proxy_type: str | None = None,
        proxy_country: str | None = None,
        profile_id: str | None = None,
        viewport: dict[str, int] | None = None,
    ) -> Session:
        """Launch a new stealth browser session."""
        body: dict[str, Any] = {"stealth": stealth}
        if proxy_type:
            proxy: dict[str, Any] = {"type": proxy_type}
            if proxy_country:
                proxy["country"] = proxy_country
            body["proxy"] = proxy
        if profile_id:
            body["profile_id"] = profile_id
        if viewport:
            body["viewport"] = viewport
        data = await self._request("POST", "/v1/sessions", json=body)
        return Session(**data)

    async def get_session(self, session_id: str) -> Session:
        """Get details about a session."""
        data = await self._request("GET", f"/v1/sessions/{session_id}")
        return Session(**data)

    async def list_sessions(self) -> SessionList:
        """List all active sessions."""
        data = await self._request("GET", "/v1/sessions")
        return SessionList(**data)

    async def destroy_session(self, session_id: str, *, save_profile: bool = False) -> None:
        """Destroy a session."""
        body = {"save_profile": True} if save_profile else None
        await self._request("DELETE", f"/v1/sessions/{session_id}", json=body)

    # --- Browser Actions ---

    async def navigate(
        self, session_id: str, url: str, *, wait_until: str = "load"
    ) -> dict[str, Any]:
        """Navigate the browser to a URL."""
        return await self._request(
            "POST",
            f"/v1/sessions/{session_id}/navigate",
            json={"url": url, "wait_until": wait_until},
        )

    async def screenshot(
        self,
        session_id: str,
        *,
        selector: str | None = None,
        full_page: bool = False,
    ) -> Screenshot:
        """Take a screenshot (returns base64 PNG)."""
        body: dict[str, Any] = {"full_page": full_page}
        if selector:
            body["selector"] = selector
        data = await self._request("POST", f"/v1/sessions/{session_id}/screenshot", json=body)
        return Screenshot(**data)

    async def click(self, session_id: str, selector: str) -> dict[str, Any]:
        """Click an element."""
        return await self._request(
            "POST", f"/v1/sessions/{session_id}/click", json={"selector": selector}
        )

    async def type_text(
        self, session_id: str, selector: str, text: str, *, clear: bool = False
    ) -> dict[str, Any]:
        """Type text into an input."""
        return await self._request(
            "POST",
            f"/v1/sessions/{session_id}/type",
            json={"selector": selector, "text": text, "clear": clear},
        )

    async def extract(
        self, session_id: str, *, selector: str | None = None, max_length: int = 5000
    ) -> dict[str, Any]:
        """Extract text content from the page."""
        body: dict[str, Any] = {"max_length": max_length}
        if selector:
            body["selector"] = selector
        return await self._request("POST", f"/v1/sessions/{session_id}/extract", json=body)

    async def execute(self, session_id: str, script: str) -> dict[str, Any]:
        """Execute JavaScript in the page."""
        return await self._request(
            "POST", f"/v1/sessions/{session_id}/execute", json={"script": script}
        )

    # --- Fleet ---

    async def create_fleet(
        self,
        count: int,
        *,
        stealth: str = "max",
        proxy_type: str | None = None,
        proxy_country: str | None = None,
    ) -> Fleet:
        """Launch multiple sessions in parallel."""
        body: dict[str, Any] = {"count": count, "stealth": stealth}
        if proxy_type:
            proxy: dict[str, Any] = {"type": proxy_type}
            if proxy_country:
                proxy["country"] = proxy_country
            body["proxy"] = proxy
        data = await self._request("POST", "/v1/fleet", json=body)
        return Fleet(**data)

    async def get_fleet(self, fleet_id: str) -> Fleet:
        """Get fleet status."""
        data = await self._request("GET", f"/v1/fleet/{fleet_id}")
        return Fleet(**data)

    async def destroy_fleet(self, fleet_id: str) -> None:
        """Destroy all sessions in a fleet."""
        await self._request("DELETE", f"/v1/fleet/{fleet_id}")

    # --- Lifecycle ---

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncMeshbrow":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
