from abc import ABC, abstractmethod
from typing import Any


class IFileStorageService(ABC):
    @abstractmethod
    async def save_file(self, file: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_file_path(self, file_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def exists(self, file_name: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def save_content(self, file_name: str, content: bytes) -> str:
        raise NotImplementedError
