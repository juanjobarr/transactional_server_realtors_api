from abc import ABC, abstractmethod
from typing import Optional


class ImageStoragePort(ABC):
    @abstractmethod
    def upload(
        self,
        *,
        content: bytes,
        content_type: str,
        filename_hint: str,
        prefix: Optional[str] = None,
        container: Optional[str] = None,
    ) -> str:
        """Upload an image and return its public URL."""

    @abstractmethod
    def delete_prefix(self, prefix: str, *, container: Optional[str] = None) -> int:
        """Delete every blob under the given prefix. Returns count of deleted blobs."""

    @abstractmethod
    def upload_from_url(
        self,
        url: str,
        *,
        prefix: str,
        filename_hint: str = "avatar",
        container: Optional[str] = None,
    ) -> str:
        """Download a remote URL and upload it to our blob storage. Returns final URL."""
