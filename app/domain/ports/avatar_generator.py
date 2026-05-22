from abc import ABC, abstractmethod
from typing import Optional


class AvatarGeneratorPort(ABC):
    @abstractmethod
    def submit(
        self,
        *,
        user_id: str,
        reference_urls: list[str],
        additional_instructions: Optional[str],
        callback_url: str,
    ) -> str:
        """Submit an avatar generation job to the external service.

        Returns the external job id used to correlate the webhook callback.
        """
