import mimetypes
import uuid
from typing import Optional

import httpx
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.config import settings
from app.domain.ports.image_storage import ImageStoragePort


_DEFAULT_EXTENSION = ".bin"


class AzureBlobImageStorage(ImageStoragePort):
    def __init__(self) -> None:
        self._service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self._container_name = settings.AZURE_STORAGE_CONTAINER_NAME

    def upload(
        self,
        *,
        content: bytes,
        content_type: str,
        filename_hint: str,
        prefix: Optional[str] = None,
        container: Optional[str] = None,
    ) -> str:
        extension = self._infer_extension(content_type, filename_hint)
        leaf = f"{uuid.uuid4().hex}{extension}"
        blob_name = f"{prefix}/{leaf}" if prefix else leaf
        container_name = container or self._container_name
        blob_client = self._service_client.get_blob_client(
            container=container_name,
            blob=blob_name,
        )
        blob_client.upload_blob(
            content,
            overwrite=False,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url

    def delete_prefix(self, prefix: str, *, container: Optional[str] = None) -> int:
        container_name = container or self._container_name
        container_client = self._service_client.get_container_client(container_name)
        count = 0
        for blob in container_client.list_blobs(name_starts_with=f"{prefix}/"):
            container_client.delete_blob(blob.name)
            count += 1
        return count

    def upload_from_url(
        self,
        url: str,
        *,
        prefix: str,
        filename_hint: str = "avatar",
        container: Optional[str] = None,
    ) -> str:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            content = response.content
            content_type = response.headers.get("content-type", "application/octet-stream")
        return self.upload(
            content=content,
            content_type=content_type,
            filename_hint=filename_hint,
            prefix=prefix,
            container=container,
        )

    @staticmethod
    def _infer_extension(content_type: str, filename_hint: str) -> str:
        if filename_hint and "." in filename_hint:
            return "." + filename_hint.rsplit(".", 1)[-1].lower()
        guessed = mimetypes.guess_extension(content_type or "")
        return guessed or _DEFAULT_EXTENSION
