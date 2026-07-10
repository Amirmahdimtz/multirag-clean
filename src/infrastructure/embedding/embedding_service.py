import hashlib
import math
import re
from typing import List

from src.core.contracts.services.i_embedding_service import IEmbeddingService


class EmbeddingService(IEmbeddingService):
    def __init__(self, dimension: int) -> None:
        self._dimension = dimension

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "hash-embedding"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        vector = [0.0 for _ in range(self._dimension)]
        tokens = self.__tokenize(text)

        if not tokens:
            return vector

        for token in tokens:
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

            index = int(token_hash[:8], 16) % self._dimension
            sign = 1.0 if int(token_hash[8:16], 16) % 2 == 0 else -1.0

            vector[index] += sign

        return self.__normalize(vector)

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]

    def __tokenize(self, text: str) -> List[str]:
        normalized = text.lower()
        return re.findall(r"\w+", normalized, flags=re.UNICODE)

    def __normalize(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(value * value for value in vector))

        if norm == 0:
            return vector

        return [value / norm for value in vector]
