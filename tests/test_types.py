"""Tests for type models."""

from meshbrow.types import Fleet, Screenshot, Session, SessionList


class TestSession:
    def test_from_kwargs(self):
        s = Session(
            id="mb_1",
            status="ready",
            cdp_endpoint="wss://example.com/cdp/mb_1",
            token="tok",
            stealth="max",
            created_at="2026-01-01T00:00:00Z",
            expires_at="2026-01-01T01:00:00Z",
        )
        assert s.id == "mb_1"
        assert s.status == "ready"
        assert s.cdp_endpoint == "wss://example.com/cdp/mb_1"

    def test_defaults(self):
        s = Session(id="mb_2", status="ready")
        assert s.cdp_endpoint == ""
        assert s.token == ""
        assert s.proxy is None

    def test_with_proxy(self):
        s = Session(id="mb_3", status="ready", proxy={"type": "residential", "country": "US"})
        assert s.proxy == {"type": "residential", "country": "US"}


class TestSessionList:
    def test_from_kwargs(self):
        sl = SessionList(
            sessions=[
                {"id": "mb_1", "status": "ready"},
                {"id": "mb_2", "status": "ready"},
            ],
            metrics={"active_sessions": 2},
        )
        assert len(sl.sessions) == 2
        assert sl.sessions[0].id == "mb_1"
        assert sl.metrics["active_sessions"] == 2

    def test_empty(self):
        sl = SessionList(sessions=[], metrics={})
        assert len(sl.sessions) == 0


class TestScreenshot:
    def test_from_kwargs(self):
        s = Screenshot(data="iVBORw0KGgo=", format="png")
        assert s.data == "iVBORw0KGgo="
        assert s.format == "png"

    def test_default_format(self):
        s = Screenshot(data="abc")
        assert s.format == "png"


class TestFleet:
    def test_from_kwargs(self):
        f = Fleet(
            id="fleet_1",
            status="ready",
            sessions=[{"id": "mb_1", "status": "ready"}],
            count=1,
        )
        assert f.id == "fleet_1"
        assert len(f.sessions) == 1
        assert f.sessions[0].id == "mb_1"
        assert f.count == 1

    def test_count_from_sessions(self):
        f = Fleet(
            id="fleet_2",
            status="ready",
            sessions=[
                {"id": "mb_1", "status": "ready"},
                {"id": "mb_2", "status": "ready"},
            ],
        )
        assert f.count == 2
