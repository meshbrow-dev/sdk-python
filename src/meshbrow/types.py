"""Type definitions for the Meshbrow SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Session:
    """A browser session."""

    id: str
    status: str
    cdp_endpoint: str = ""
    token: str = ""
    stealth: str = ""
    created_at: str = ""
    expires_at: str = ""
    proxy: dict[str, Any] | None = None

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", "")
        self.status = kwargs.get("status", "")
        self.cdp_endpoint = kwargs.get("cdp_endpoint", "")
        self.token = kwargs.get("token", "")
        self.stealth = kwargs.get("stealth", "")
        self.created_at = kwargs.get("created_at", "")
        self.expires_at = kwargs.get("expires_at", "")
        self.proxy = kwargs.get("proxy")


@dataclass
class SessionList:
    """List of sessions with metrics."""

    sessions: list[Session]
    metrics: dict[str, Any]

    def __init__(self, **kwargs: Any) -> None:
        raw_sessions = kwargs.get("sessions", [])
        self.sessions = [Session(**s) if isinstance(s, dict) else s for s in raw_sessions]
        self.metrics = kwargs.get("metrics", {})


@dataclass
class Screenshot:
    """A screenshot result."""

    data: str  # base64-encoded PNG
    format: str = "png"

    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs.get("data", "")
        self.format = kwargs.get("format", "png")


@dataclass
class Fleet:
    """A fleet of browser sessions."""

    id: str
    status: str
    sessions: list[Session]
    count: int = 0

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", "")
        self.status = kwargs.get("status", "")
        raw_sessions = kwargs.get("sessions", [])
        self.sessions = [Session(**s) if isinstance(s, dict) else s for s in raw_sessions]
        self.count = kwargs.get("count", len(self.sessions))
