from typing import List
from uuid import UUID

from src.domain.models.document_chunk import DocumentChunk
from src.infrastructure.document_processing.text_extractor import TextExtractor
from src.infrastructure.document_processing.text_splitter import TextSplitter


class DocumentProcessingService:
    def __init__(
        self,
        text_extractor: TextExtractor,
        text_splitter: TextSplitter,
    ) -> None:
        self.text_extractor = text_extractor
        self.text_splitter = text_splitter

    def process_file(
        self,
        dataset_id: UUID,
        file_path: str,
    ) -> List[DocumentChunk]:
        text = self.text_extractor.extract(file_path)
        chunks = self.text_splitter.split(text)

        return [
            DocumentChunk(
                dataset_id=dataset_id,
                content=chunk,
                chunk_index=index,
                token_count=None,
                metadata={
                    "source_file_path": file_path,
                },
            )
            for index, chunk in enumerate(chunks)
        ]
