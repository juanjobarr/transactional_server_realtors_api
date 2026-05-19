import mimetypes
import uuid

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

    def upload(self, *, content: bytes, content_type: str, filename_hint: str) -> str:
        extension = self._infer_extension(content_type, filename_hint)
        blob_name = f"{uuid.uuid4().hex}{extension}"
        blob_client = self._service_client.get_blob_client(
            container=self._container_name,
            blob=blob_name,
        )
        blob_client.upload_blob(
            content,
            overwrite=False,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url

    @staticmethod
    def _infer_extension(content_type: str, filename_hint: str) -> str:
        if filename_hint and "." in filename_hint:
            return "." + filename_hint.rsplit(".", 1)[-1].lower()
        guessed = mimetypes.guess_extension(content_type or "")
        return guessed or _DEFAULT_EXTENSION
