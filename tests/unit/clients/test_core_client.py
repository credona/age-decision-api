import pytest
from httpx import Response
from httpx._transports.base import AsyncBaseTransport
from httpx import AsyncClient, Request

from app.infrastructure.clients.core_client import CoreClient


class MockTransport(AsyncBaseTransport):
    async def handle_async_request(self, request: Request) -> Response:
        return Response(
            status_code=200,
            json={
                "decision": "match",
                "threshold": {
                    "type": "minimum_age",
                    "value": 18,
                    "source": "majority_country",
                    "majority_country": "FR",
                },
                "cred_decision_score": {
                    "score": 0.88,
                    "level": "high",
                },
            },
        )


@pytest.mark.asyncio
async def test_core_client_estimate_image():
    client = CoreClient()

    transport = MockTransport()

    async with AsyncClient(transport=transport) as http_client:
        client._client = http_client

        result = await client.estimate_image(
            file_content=b"fake",
            filename="test.jpg",
            content_type="image/jpeg",
            headers={},
        )

    assert result["decision"] == "match"
    assert result["threshold"]["majority_country"] == "FR"
    assert result["cred_decision_score"]["score"] == 0.88
