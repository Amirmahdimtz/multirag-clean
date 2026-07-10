import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.core.contracts.services.i_file_storage_service import (
    IFileStorageService,
)


class FileStorageService(IFileStorageService):
    def __init__(
        self,
        base_path: str,
    ) -> None:
        self.base_path = base_path

        os.makedirs(
            self.base_path,
            exist_ok=True,
        )

    async def save_file(
        self,
        file: Any,
    ) -> str:
        storage_file_name = self.__generate_storage_file_name(
            file.filename
        )

        file_path = os.path.join(
            self.base_path,
            storage_file_name,
        )

        content = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return storage_file_name

    async def save_content(
        self,
        file_name: str,
        content: bytes,
    ) -> str:
        storage_file_name = self.__generate_storage_file_name(
            file_name
        )

        file_path = os.path.join(
            self.base_path,
            storage_file_name,
        )

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return storage_file_name

    def get_file_path(
        self,
        file_name: str,
    ) -> str:
        return os.path.join(
            self.base_path,
            file_name,
        )

    def exists(
        self,
        file_name: str,
    ) -> bool:
        return os.path.exists(
            self.get_file_path(file_name)
        )

    def __generate_storage_file_name(
        self,
        file_name: str,
    ) -> str:
        extension = Path(
            file_name
        ).suffix.lower()

        return f"{uuid4().hex}{extension}"
