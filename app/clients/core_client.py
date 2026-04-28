import httpx

from app.config.settings import settings


class CoreClient:
    """
    Client responsible for interacting with age-decision-core service.

    Supports dependency injection of an httpx.AsyncClient for testing.
    """

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def estimate_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        headers: dict[str, str],
        params: dict | None = None,
    ) -> dict:
        files = {
            "file": (
                filename,
                file_content,
                content_type or "application/octet-stream",
            )
        }

        client = self._client

        if client:
            response = await client.post(
                f"{settings.age_decision_core_url}/estimate",
                files=files,
                headers=headers,
                params=params or {},
            )
            self._raise_for_status(response, "core")
            return response.json()

        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds
        ) as http_client:
            response = await http_client.post(
                f"{settings.age_decision_core_url}/estimate",
                files=files,
                headers=headers,
                params=params or {},
            )
            self._raise_for_status(response, "core")
            return response.json()

    def _raise_for_status(self, response: httpx.Response, service: str) -> None:
        """
        Raise a stable downstream error without exposing response internals.
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"{service}_request_failed status={response.status_code}"
            ) from exc


core_client = CoreClient()
