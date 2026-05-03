from typing import Protocol


class CoreClientPort(Protocol):
    async def estimate_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        headers: dict[str, str],
        params: dict | None = None,
    ) -> dict: ...

    async def health_check(self) -> dict[str, str]: ...
