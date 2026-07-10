from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from src.domain.models.document_chunk import (
    DocumentChunk,
)


class IDocumentProcessingService(
    ABC
):
    @abstractmethod
    def process_file(
        self,
        dataset_id: UUID,
        file_path: str,
    ) -> List[DocumentChunk]:
        raise NotImplementedError
