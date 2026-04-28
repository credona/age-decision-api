import pytest
from httpx import Response
from httpx._transports.base import AsyncBaseTransport
from httpx import AsyncClient, Request

from app.clients.antispoof_client import AntispoofClient


class MockTransport(AsyncBaseTransport):
    async def handle_async_request(self, request: Request) -> Response:
        return Response(
            status_code=200,
            json={"decision": "real", "is_real": True},
        )


@pytest.mark.asyncio
async def test_antispoof_client_check_image():
    client = AntispoofClient()

    transport = MockTransport()

    async with AsyncClient(transport=transport) as http_client:
        client._client = http_client

        result = await client.check_image(
            file_content=b"fake",
            filename="test.jpg",
            content_type="image/jpeg",
            headers={},
        )

    assert result["decision"] == "real"
