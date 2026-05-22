from typing import Optional

import httpx

from app.config import settings
from app.domain.ports.avatar_generator import AvatarGeneratorPort


class HttpAvatarGenerator(AvatarGeneratorPort):
    """HTTP client for our internal avatar generation service.

    No auth required (internal service). The service responds immediately and
    processes asynchronously; results are delivered back via webhook.
    """

    def __init__(self) -> None:
        self._url = settings.AVATAR_SERVICE_URL
        self._timeout = settings.AVATAR_SERVICE_TIMEOUT_SECONDS

    def submit(
        self,
        *,
        user_id: str,
        reference_urls: list[str],
        additional_instructions: Optional[str],
        callback_url: str,
    ) -> str:
        payload = {
            "user_id": user_id,
            "reference_urls": reference_urls,
            "additional_instructions": additional_instructions or "",
            "callback_url": callback_url,
        }
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(self._url, json=payload)
            response.raise_for_status()
            data = response.json()

        external_job_id = data.get("job_id") or data.get("external_job_id")
        if not external_job_id:
            raise ValueError(
                "Avatar service response is missing 'job_id' / 'external_job_id'"
            )
        return str(external_job_id)
