"""Tests for the synchronous Meshbrow client."""

import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from meshbrow import Meshbrow, Session, SessionList, Screenshot, Fleet


BASE_URL = "https://api.meshbrow.dev"


@pytest.fixture
def client():
    c = Meshbrow(api_key="test-key", base_url=BASE_URL)
    yield c
    c.close()


class TestCreateSession:
    def test_basic_create(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={
                "data": {
                    "id": "mb_abc123",
                    "status": "ready",
                    "cdp_endpoint": "wss://api.meshbrow.dev/cdp/mb_abc123?token=tok",
                    "token": "tok",
                    "created_at": "2026-06-14T00:00:00Z",
                    "expires_at": "2026-06-14T01:00:00Z",
                }
            },
            status_code=201,
        )

        session = client.create_session()
        assert isinstance(session, Session)
        assert session.id == "mb_abc123"
        assert session.status == "ready"
        assert session.cdp_endpoint == "wss://api.meshbrow.dev/cdp/mb_abc123?token=tok"

        # Verify request body
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["stealth"] == "max"

    def test_create_with_proxy(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"data": {"id": "mb_proxy1", "status": "ready"}},
            status_code=201,
        )

        session = client.create_session(
            proxy_type="residential", proxy_country="US", stealth="standard"
        )
        assert session.id == "mb_proxy1"

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["proxy"] == {"type": "residential", "country": "US"}
        assert body["stealth"] == "standard"

    def test_create_with_profile(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"data": {"id": "mb_prof1", "status": "ready"}},
            status_code=201,
        )

        session = client.create_session(profile_id="prof_123")
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["profile_id"] == "prof_123"

    def test_create_with_viewport(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"data": {"id": "mb_vp1", "status": "ready"}},
            status_code=201,
        )

        session = client.create_session(viewport={"width": 1920, "height": 1080})
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["viewport"] == {"width": 1920, "height": 1080}


class TestGetSession:
    def test_get(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions/mb_abc123",
            json={
                "data": {
                    "id": "mb_abc123",
                    "status": "ready",
                    "stealth": "max",
                    "created_at": "2026-06-14T00:00:00Z",
                    "expires_at": "2026-06-14T01:00:00Z",
                }
            },
        )

        session = client.get_session("mb_abc123")
        assert session.id == "mb_abc123"
        assert session.stealth == "max"


class TestListSessions:
    def test_list(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions",
            json={
                "sessions": [
                    {"id": "mb_1", "status": "ready", "created_at": "2026-06-14T00:00:00Z"},
                    {"id": "mb_2", "status": "ready", "created_at": "2026-06-14T00:01:00Z"},
                ],
                "metrics": {"active_sessions": 2, "sessions_today": 5},
            },
        )

        result = client.list_sessions()
        assert isinstance(result, SessionList)
        assert len(result.sessions) == 2
        assert result.sessions[0].id == "mb_1"
        assert result.metrics["active_sessions"] == 2


class TestDestroySession:
    def test_destroy(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/v1/sessions/mb_abc123",
            status_code=204,
        )

        client.destroy_session("mb_abc123")
        request = httpx_mock.get_requests()[0]
        assert request.method == "DELETE"

    def test_destroy_with_save_profile(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/v1/sessions/mb_abc123",
            status_code=204,
        )

        client.destroy_session("mb_abc123", save_profile=True)
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["save_profile"] is True


class TestNavigate:
    def test_navigate(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/navigate",
            json={"data": {"url": "https://example.com", "title": "Example", "status": 200}},
        )

        result = client.navigate("mb_1", "https://example.com")
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example"

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["url"] == "https://example.com"
        assert body["wait_until"] == "load"

    def test_navigate_with_wait_until(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/navigate",
            json={"data": {"url": "https://example.com", "title": "Example", "status": 200}},
        )

        client.navigate("mb_1", "https://example.com", wait_until="networkidle")
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["wait_until"] == "networkidle"


class TestScreenshot:
    def test_screenshot(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/screenshot",
            json={"data": {"data": "iVBORw0KGgo=", "format": "png"}},
        )

        result = client.screenshot("mb_1")
        assert isinstance(result, Screenshot)
        assert result.data == "iVBORw0KGgo="
        assert result.format == "png"

    def test_screenshot_with_selector(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/screenshot",
            json={"data": {"data": "abc123", "format": "png"}},
        )

        client.screenshot("mb_1", selector="#main", full_page=True)
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["selector"] == "#main"
        assert body["full_page"] is True


class TestClick:
    def test_click(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/click",
            json={"data": {"clicked": True}},
        )

        client.click("mb_1", "button.submit")
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["selector"] == "button.submit"


class TestTypeText:
    def test_type(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/type",
            json={"data": {"typed": True}},
        )

        client.type_text("mb_1", "input#email", "test@example.com", clear=True)
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["selector"] == "input#email"
        assert body["text"] == "test@example.com"
        assert body["clear"] is True


class TestExtract:
    def test_extract(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/extract",
            json={"data": {"text": "Hello World"}},
        )

        result = client.extract("mb_1")
        assert result["text"] == "Hello World"

    def test_extract_with_selector(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/extract",
            json={"data": {"text": "Content"}},
        )

        client.extract("mb_1", selector="article", max_length=1000)
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["selector"] == "article"
        assert body["max_length"] == 1000


class TestExecute:
    def test_execute(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/execute",
            json={"data": {"result": 42}},
        )

        result = client.execute("mb_1", "return 21 * 2")
        assert result["result"] == 42


class TestFleet:
    def test_create_fleet(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/fleet",
            json={
                "data": {
                    "id": "fleet_abc",
                    "status": "ready",
                    "sessions": [
                        {"id": "mb_1", "status": "ready"},
                        {"id": "mb_2", "status": "ready"},
                    ],
                    "count": 2,
                }
            },
            status_code=201,
        )

        fleet = client.create_fleet(2, proxy_type="residential", proxy_country="GB")
        assert isinstance(fleet, Fleet)
        assert fleet.id == "fleet_abc"
        assert len(fleet.sessions) == 2

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["count"] == 2
        assert body["proxy"] == {"type": "residential", "country": "GB"}

    def test_get_fleet(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/fleet/fleet_abc",
            json={
                "data": {
                    "id": "fleet_abc",
                    "status": "ready",
                    "sessions": [{"id": "mb_1", "status": "ready"}],
                    "count": 1,
                }
            },
        )

        fleet = client.get_fleet("fleet_abc")
        assert fleet.id == "fleet_abc"

    def test_destroy_fleet(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/v1/fleet/fleet_abc",
            status_code=204,
        )

        client.destroy_fleet("fleet_abc")


class TestErrorHandling:
    def test_401_raises(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions/mb_1",
            json={"error": {"code": "unauthorized", "message": "Invalid API key"}},
            status_code=401,
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            client.get_session("mb_1")
        assert exc_info.value.response.status_code == 401

    def test_404_raises(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions/nonexistent",
            json={"error": {"code": "not_found", "message": "session not found"}},
            status_code=404,
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            client.get_session("nonexistent")
        assert exc_info.value.response.status_code == 404

    def test_500_raises(self, client: Meshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"error": {"code": "internal", "message": "internal error"}},
            status_code=500,
        )

        with pytest.raises(httpx.HTTPStatusError):
            client.create_session()


class TestAuth:
    def test_auth_header(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions",
            json={"sessions": [], "metrics": {}},
        )

        client = Meshbrow(api_key="sk_test_123", base_url=BASE_URL)
        client.list_sessions()

        request = httpx_mock.get_requests()[0]
        assert request.headers["authorization"] == "Bearer sk_test_123"
        assert request.headers["user-agent"] == "meshbrow-python/0.1.0"
        client.close()


class TestContextManager:
    def test_context_manager(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions",
            json={"sessions": [], "metrics": {}},
        )

        with Meshbrow(api_key="test", base_url=BASE_URL) as client:
            client.list_sessions()
