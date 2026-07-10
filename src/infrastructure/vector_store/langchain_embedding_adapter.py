from typing import List

from langchain_core.embeddings import Embeddings

from src.core.contracts.services.i_embedding_service import IEmbeddingService


class LangChainEmbeddingAdapter(Embeddings):
    def __init__(self, embedding_service: IEmbeddingService) -> None:
        self._embedding_service = embedding_service

    @property
    def provider_name(self) -> str:
        return self._embedding_service.provider_name

    @property
    def model_name(self) -> str:
        return self._embedding_service.model_name

    @property
    def dimension(self) -> int:
        return self._embedding_service.dimension

    def embed_query(self, text: str) -> List[float]:
        embedding = self._embedding_service.embed_text(text)

        self.__validate_embedding_dimension(embedding)

        return embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._embedding_service.embed_many(texts)

        for embedding in embeddings:
            self.__validate_embedding_dimension(embedding)

        return embeddings

    async def aembed_query(self, text: str) -> List[float]:
        return self.embed_query(text)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embed_documents(texts)

    def __validate_embedding_dimension(self, embedding: List[float]) -> None:
        if len(embedding) != self._embedding_service.dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self._embedding_service.dimension}, "
                f"got {len(embedding)}"
            )
