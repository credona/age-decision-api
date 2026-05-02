from typing import Protocol


class AntispoofClientPort(Protocol):
    async def check_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        headers: dict[str, str],
    ) -> dict: ...
