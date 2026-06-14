"""Tests for the async Meshbrow client."""

import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from meshbrow import AsyncMeshbrow, Session, Screenshot, Fleet


BASE_URL = "https://api.meshbrow.dev"


@pytest.fixture
def client():
    return AsyncMeshbrow(api_key="test-key", base_url=BASE_URL)


class TestAsyncCreateSession:
    async def test_basic_create(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"data": {"id": "mb_async1", "status": "ready"}},
            status_code=201,
        )

        session = await client.create_session()
        assert session.id == "mb_async1"
        assert session.status == "ready"
        await client.close()

    async def test_create_with_proxy(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions",
            json={"data": {"id": "mb_async2", "status": "ready"}},
            status_code=201,
        )

        session = await client.create_session(proxy_type="datacenter", proxy_country="DE")
        assert session.id == "mb_async2"

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["proxy"] == {"type": "datacenter", "country": "DE"}
        await client.close()


class TestAsyncNavigate:
    async def test_navigate(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/navigate",
            json={"data": {"url": "https://example.com", "title": "Example", "status": 200}},
        )

        result = await client.navigate("mb_1", "https://example.com")
        assert result["title"] == "Example"
        await client.close()


class TestAsyncScreenshot:
    async def test_screenshot(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/sessions/mb_1/screenshot",
            json={"data": {"data": "iVBORw0KGgo=", "format": "png"}},
        )

        result = await client.screenshot("mb_1")
        assert isinstance(result, Screenshot)
        assert result.data == "iVBORw0KGgo="
        await client.close()


class TestAsyncFleet:
    async def test_create_fleet(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/v1/fleet",
            json={
                "data": {
                    "id": "fleet_async",
                    "status": "ready",
                    "sessions": [{"id": "mb_1", "status": "ready"}],
                    "count": 1,
                }
            },
            status_code=201,
        )

        fleet = await client.create_fleet(1)
        assert fleet.id == "fleet_async"
        await client.close()

    async def test_destroy_fleet(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/v1/fleet/fleet_abc",
            status_code=204,
        )

        await client.destroy_fleet("fleet_abc")
        await client.close()


class TestAsyncContextManager:
    async def test_context_manager(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v1/sessions",
            json={"sessions": [], "metrics": {}},
        )

        async with AsyncMeshbrow(api_key="test", base_url=BASE_URL) as client:
            await client.list_sessions()


class TestAsyncDestroy:
    async def test_destroy(self, client: AsyncMeshbrow, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/v1/sessions/mb_1",
            status_code=204,
        )

        await client.destroy_session("mb_1")
        await client.close()
