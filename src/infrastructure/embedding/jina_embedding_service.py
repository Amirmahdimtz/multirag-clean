import os
from pathlib import Path
from typing import List

import torch
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.contracts.services.i_embedding_service import IEmbeddingService


class JinaEmbeddingService(IEmbeddingService):
    def __init__(
        self,
        model_name: str,
        vector_size: int,
        offline: bool,
        local_model_path: str | None = None,
        normalize_embeddings: bool = False,
        device: str = "cpu",
    ) -> None:
        self._model_name = model_name
        self._dimension = vector_size

        if offline:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

        resolved_device = self.__resolve_device(device)

        resolved_model_name = self.__resolve_model_name(
            model_name=model_name,
            local_model_path=local_model_path,
            offline=offline,
        )

        model_kwargs = {
            "device": resolved_device,
            "trust_remote_code": True,
        }

        if offline:
            model_kwargs["local_files_only"] = True

        encode_kwargs = {
            "normalize_embeddings": normalize_embeddings,
        }

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=resolved_model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )

    @property
    def provider_name(self) -> str:
        return "jina"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        embedding = self.embedding_model.embed_query(text)
        self.__validate_dimension(embedding)
        return embedding

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.embedding_model.embed_documents(texts)

        for embedding in embeddings:
            self.__validate_dimension(embedding)

        return embeddings

    def __resolve_model_name(
        self,
        model_name: str,
        local_model_path: str | None,
        offline: bool,
    ) -> str:
        if not offline:
            return model_name

        if local_model_path is None:
            raise ValueError(
                "local_model_path is required when embedding.offline is true"
            )

        path = Path(local_model_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Local embedding model path not found: {path}"
            )

        return str(path)

    def __resolve_device(self, device: str) -> str:
        normalized_device = device.strip().lower()

        if normalized_device not in {"auto", "cpu", "cuda"}:
            raise ValueError(
                "Embedding device must be one of: auto, cpu, cuda"
            )

        if normalized_device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"

        if normalized_device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(
                "Embedding device is set to cuda, but CUDA is unavailable"
            )

        return normalized_device

    def __validate_dimension(self, embedding: List[float]) -> None:
        if len(embedding) != self._dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self._dimension}, got {len(embedding)}"
            )
