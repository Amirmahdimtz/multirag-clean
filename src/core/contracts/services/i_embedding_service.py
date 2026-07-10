from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_many(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError
