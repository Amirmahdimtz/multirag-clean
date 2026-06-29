from dataclasses import dataclass

from src.domain.models.vector_document import VectorDocument


@dataclass
class VectorSearchResult:
    document: VectorDocument
    score: float
