from uuid import UUID

from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.enums.dataset_type import DatasetType
from src.domain.models.dataset import Dataset
from src.domain.models.vector_document import VectorDocument


class DatasetBusiness:
    def __init__(
        self,
        dataset_repository,
        file_storage_service,
        document_processing_service,
        embedding_service,
        vector_store_service,
    ) -> None:
        self.dataset_repository = dataset_repository
        self.file_storage_service = file_storage_service
        self.document_processing_service = document_processing_service
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service

    async def upload_dataset(self, name: str, file) -> Dataset:
        file_name = await self.file_storage_service.save_file(file)

        dataset = Dataset(
            name=name,
            file_name=file_name,
            dataset_type=DatasetType.UNKNOWN,
            content_type=getattr(file, "content_type", None),
            is_vectorized=False,
        )

        return await self.dataset_repository.add(dataset)

    async def get_all(self):
        return await self.dataset_repository.get_all()

    async def get_by_id(self, dataset_id: UUID):
        dataset = await self.dataset_repository.get_by_id(Dataset, str(dataset_id))

        if dataset is None:
            raise NotFoundException("Dataset not found")

        return dataset

    async def delete(self, dataset: Dataset):
        self.vector_store_service.delete_dataset(dataset.id)
        return await self.dataset_repository.delete(dataset)

    async def preview_chunks(self, dataset_id: UUID, limit: int = 5):
        chunks = await self.__build_chunks(dataset_id)
        return chunks[:limit]

    async def count_chunks(self, dataset_id: UUID) -> int:
        chunks = await self.__build_chunks(dataset_id)
        return len(chunks)

    async def vectorize_dataset(self, dataset_id: UUID) -> int:
        dataset = await self.get_by_id(dataset_id)
        chunks = await self.__build_chunks(dataset_id)

        vector_documents = []

        for chunk in chunks:
            embedding = self.embedding_service.embed_text(chunk.content)

            vector_documents.append(
                VectorDocument(
                    dataset_id=dataset.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=embedding,
                    metadata=chunk.metadata,
                )
            )

        vector_count = self.vector_store_service.upsert_documents(
            dataset_id=dataset.id,
            documents=vector_documents,
        )

        dataset.mark_as_vectorized()
        await self.dataset_repository.update(dataset)

        return vector_count

    async def search_dataset(
        self,
        dataset_id: UUID,
        query: str,
        limit: int = 5,
    ):
        dataset = await self.get_by_id(dataset_id)

        if not dataset.is_vectorized:
            raise NotFoundException("Dataset is not vectorized yet")

        if self.vector_store_service.count_documents(dataset.id) == 0:
            raise NotFoundException(
                "Vector index not found. Please vectorize dataset again."
            )

        query_embedding = self.embedding_service.embed_text(query)

        return self.vector_store_service.similarity_search(
            dataset_id=dataset.id,
            query_embedding=query_embedding,
            limit=limit,
        )

    async def __build_chunks(self, dataset_id: UUID):
        dataset = await self.get_by_id(dataset_id)

        if not self.file_storage_service.exists(dataset.file_name):
            raise NotFoundException("Dataset file not found")

        file_path = self.file_storage_service.get_file_path(dataset.file_name)

        return self.document_processing_service.process_file(
            dataset_id=dataset.id,
            file_path=file_path,
        )
