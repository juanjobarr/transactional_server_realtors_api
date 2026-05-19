from abc import ABC, abstractmethod


class ImageStoragePort(ABC):
    @abstractmethod
    def upload(self, *, content: bytes, content_type: str, filename_hint: str) -> str:
        """Upload an image and return its public URL."""
