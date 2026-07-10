from typing import List
from uuid import UUID

from pathlib import Path

from src.domain.models.document_chunk import DocumentChunk
from src.infrastructure.document_processing.text_extractor import TextExtractor
from src.infrastructure.document_processing.text_splitter import TextSplitter
from src.core.contracts.services.i_document_processing_service import (
    IDocumentProcessingService,
)


class DocumentProcessingService(IDocumentProcessingService):
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

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        if extension == ".csv":
            return self.__process_csv(
                dataset_id=dataset_id,
                file_path=file_path,
            )

        text = self.text_extractor.extract(
            file_path
        )

        chunks = self.text_splitter.split(
            text
        )

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
            for index, chunk in enumerate(
                chunks
            )
        ]

    def __process_csv(
        self,
        dataset_id: UUID,
        file_path: str,
    ) -> List[DocumentChunk]:

        rows = (
            self.text_extractor
            .extract_csv_rows(
                file_path
            )
        )

        return [
            DocumentChunk(
                dataset_id=dataset_id,

                content=question,

                chunk_index=index,

                token_count=None,

                metadata={
                    "answer": answer,

                    "csv_row_number": (
                        row_number
                    ),

                    "source_file_path": (
                        file_path
                    ),
                },
            )
            for index, (
                question,
                answer,
                row_number,
            ) in enumerate(rows)
        ]
