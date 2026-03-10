import pytest
from httpx import AsyncClient

pytestmark = [
    pytest.mark.integration,
    pytest.mark.usefixtures("_integration_state"),
]


@pytest.mark.asyncio
async def test_health_endpoints_available(client: AsyncClient):
    root = await client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "operating"

    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "operating"


@pytest.mark.asyncio
async def test_readiness_endpoint_available(client: AsyncClient):
    ready = await client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
