import pytest
from httpx import Response
from httpx._transports.base import AsyncBaseTransport
from httpx import AsyncClient, Request

from app.clients.core_client import CoreClient


class MockTransport(AsyncBaseTransport):
    async def handle_async_request(self, request: Request) -> Response:
        return Response(
            status_code=200,
            json={"decision": "adult", "is_adult": True},
        )


@pytest.mark.asyncio
async def test_core_client_estimate_image():
    client = CoreClient()

    transport = MockTransport()

    async with AsyncClient(transport=transport) as http_client:
        # Monkeypatch simple
        client._client = http_client

        result = await client.estimate_image(
            file_content=b"fake",
            filename="test.jpg",
            content_type="image/jpeg",
            headers={},
        )

    assert result["decision"] == "adult"