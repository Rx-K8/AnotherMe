from httpx import AsyncClient


class TestHealthCheck:
    async def test_health_check_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_health_check_content_type(self, client: AsyncClient) -> None:
        response = await client.get("/api/health")
        assert response.headers["content-type"] == "application/json"
