from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from app.routing.analyze import router
from app.depends import get_inspector, get_links_collection

app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_inspect_url(monkeypatch):
    inspector = AsyncMock()
    inspector.check_status.return_value = (200, {"content-type": "text/html"})
    inspector.measure_response_time.return_value = 0.123
    inspector.check_ssl.return_value = {"valid": True, "expires": "2030-01-01T00:00:00", "issuer": {}, "subject": {}}
    inspector.get_redirects.return_value = ["https://example.com"]

    class MockCollection:
        async def insert_one(self, data):
            return True

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    app.dependency_overrides[get_inspector] = lambda: inspector
    app.dependency_overrides[get_links_collection] = lambda: MockCollection()

    monkeypatch.setattr("app.routing.analyze.redis_client", mock_redis)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"link": "https://example.com", "follow_redirects": True}
        response = await ac.post("/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert data["ssl"] is True
    assert data["response_time"] == 0.123
    assert data["content_type"] == "text/html"
    assert data["redirects"] == ["https://example.com"]

    def normalize(url):
        return str(url).rstrip("/")

    assert normalize(inspector.check_status.call_args[0][0]) == "https://example.com"
    assert normalize(inspector.measure_response_time.call_args[0][0]) == "https://example.com"
    assert normalize(inspector.check_ssl.call_args[0][0]) == "https://example.com"
    args, kwargs = inspector.get_redirects.call_args
    assert normalize(args[0]) == "https://example.com"
    assert kwargs.get("follow_redirects") is True

    mock_redis.get.assert_called_once()
    mock_redis.set.assert_called_once()
