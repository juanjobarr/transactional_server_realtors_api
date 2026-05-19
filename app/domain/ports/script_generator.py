from abc import ABC, abstractmethod
from typing import Optional


class ScriptGeneratorPort(ABC):
    @abstractmethod
    def generate(
        self,
        *,
        topic_code: str,
        topic_label: str,
        title: Optional[str],
        notes: Optional[str],
        tone: str,
        reference_image_bytes: Optional[bytes] = None,
        reference_image_mime: Optional[str] = None,
    ) -> str: ...
