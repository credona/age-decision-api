from app.application.dto.verify_command import VerifyCommand
from app.application.use_cases.verification_orchestrator import VerificationOrchestrator


class RunVerificationUseCase:
    """
    Application use case for public verification.

    The API layer owns HTTP request parsing and public response filtering.
    The decision service currently owns orchestration and will be split next.
    """

    def __init__(self, service: VerificationOrchestrator):
        self.service = service

    async def execute(self, command: VerifyCommand) -> dict:
        return await self.service.verify_image_base64(
            image_base64=command.image_base64,
            request_id=command.request_id,
            correlation_id=command.correlation_id,
            majority_country=command.majority_country,
            age_threshold=command.age_threshold,
        )
