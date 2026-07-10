from uuid import UUID
from pathlib import Path

from src.core.contracts.repositories.i_dataset_repository import IDatasetRepository
from src.core.contracts.services.i_embedding_service import IEmbeddingService
from src.core.contracts.services.i_file_storage_service import IFileStorageService
from src.core.contracts.services.i_vector_store_service import IVectorStoreService
from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.enums.dataset_type import DatasetType
from src.domain.models.dataset import Dataset
from src.domain.models.vector_document import VectorDocument
from src.core.contracts.services.i_document_processing_service import (
    IDocumentProcessingService,
)
from src.core.exceptions.file_too_large_exception import (
    FileTooLargeException,
)

from src.core.exceptions.unsupported_file_extension_exception import (
    UnsupportedFileExtensionException,
)


class DatasetBusiness:
    def __init__(
        self,
        dataset_repository: IDatasetRepository,
        file_storage_service: IFileStorageService,
        document_processing_service: IDocumentProcessingService,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        allowed_extensions: list[str],
        max_file_size_mb: float,
        default_k_retrieval: int,
        default_score_threshold: float | None,
    ) -> None:
        self.dataset_repository = (
            dataset_repository
        )

        self.file_storage_service = (
            file_storage_service
        )

        self.document_processing_service = (
            document_processing_service
        )

        self.embedding_service = (
            embedding_service
        )

        self.vector_store_service = (
            vector_store_service
        )

        if not isinstance(
            allowed_extensions,
            (list, tuple, set),
        ):
            raise ValueError(
                "uploads.allowed_extensions "
                "must be a list, tuple, or set"
            )

        normalized_extensions = {
            str(extension)
            .strip()
            .lower()
            .lstrip(".")
            for extension in allowed_extensions
        }

        self.allowed_extensions = {
            extension
            for extension in normalized_extensions
            if extension
        }

        if not self.allowed_extensions:
            raise ValueError(
                "uploads.allowed_extensions "
                "must contain at least "
                "one extension"
            )

        self.max_file_size_mb = float(
            max_file_size_mb
        )

        if self.max_file_size_mb <= 0:
            raise ValueError(
                "uploads.max_file_size_mb "
                "must be greater than zero"
            )

        self.max_file_size_bytes = int(
            self.max_file_size_mb
            * 1024
            * 1024
        )

        self.default_k_retrieval = int(
            default_k_retrieval
        )

        if self.default_k_retrieval <= 0:
            raise ValueError(
                "rag.k_retrieval "
                "must be greater than zero"
            )

        self.default_score_threshold = (
            None
            if default_score_threshold is None
            else float(
                default_score_threshold
            )
        )

        self.__validate_score_threshold(
            self.default_score_threshold
        )

    async def upload_dataset(
        self,
        name: str,
        file,
        scope: DatasetScope = DatasetScope.ADMIN,
        owner_user_id: UUID | None = None,
        admin_id: UUID | None = None,
        expertise: str | None = None,
    ) -> Dataset:
        self.__validate_dataset_ownership(
            scope=scope,
            owner_user_id=owner_user_id,
        )

        raw_file_name = getattr(
            file,
            "filename",
            None,
        )

        if not raw_file_name:
            raise BadRequestException(
                "File name is required."
            )

        original_file_name = Path(
            str(raw_file_name)
            .replace("\\", "/")
        ).name

        extension = (
            Path(original_file_name)
            .suffix
            .lower()
            .lstrip(".")
        )

        if (
            extension
            not in self.allowed_extensions
        ):
            raise (
                UnsupportedFileExtensionException(
                    allowed_extensions=sorted(
                        self.allowed_extensions
                    )
                )
            )

        try:
            dataset_type = DatasetType(
                extension
            )

        except ValueError as exception:
            raise (
                UnsupportedFileExtensionException(
                    allowed_extensions=sorted(
                        self.allowed_extensions
                    )
                )
            ) from exception

        if (
            dataset_type
            == DatasetType.UNKNOWN
        ):
            raise (
                UnsupportedFileExtensionException(
                    allowed_extensions=sorted(
                        self.allowed_extensions
                    )
                )
            )

        content = await file.read(
            self.max_file_size_bytes + 1
        )

        if (
            len(content)
            > self.max_file_size_bytes
        ):
            raise FileTooLargeException(
                max_file_size_mb=(
                    self.max_file_size_mb
                )
            )

        file_size_mb = round(
            len(content)
            / (1024 * 1024),
            2,
        )

        storage_file_name = (
            await self.file_storage_service
            .save_content(
                file_name=(
                    original_file_name
                ),
                content=content,
            )
        )

        dataset = Dataset(
            name=name,

            file_name=(
                original_file_name
            ),

            storage_file_name=(
                storage_file_name
            ),

            dataset_type=dataset_type,

            scope=scope,

            owner_user_id=(
                owner_user_id
            ),

            content_type=getattr(
                file,
                "content_type",
                None,
            ),

            file_size_mb=(
                file_size_mb
            ),

            content=content,

            expertise=expertise,

            admin_id=admin_id,

            is_vectorized=False,
        )

        return (
            await self.dataset_repository
            .add(
                dataset
            )
        )

    async def get_all(self):
        return await self.dataset_repository.get_all()

    async def get_by_id(
        self,
        dataset_id: UUID,
    ) -> Dataset:
        dataset = await self.dataset_repository.get_by_id(dataset_id)

        if dataset is None:
            raise NotFoundException("Dataset not found")

        return dataset

    async def get_by_owner_user_id(self, owner_user_id: UUID) -> list[Dataset]:
        return await self.dataset_repository.get_by_owner_user_id(owner_user_id)

    async def delete(self, dataset: Dataset):
        await self.vector_store_service.delete_dataset(dataset.id)
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

        vector_count = await self.vector_store_service.upsert_documents(
            dataset_id=dataset.id,
            documents=vector_documents,
        )

        dataset.mark_as_vectorized(
            embedding_provider=self.embedding_service.provider_name,
            embedding_model=self.embedding_service.model_name,
            embedding_dimension=self.embedding_service.dimension,
        )
        await self.dataset_repository.update(dataset)

        return vector_count

    async def search_dataset(
        self,
        dataset_id: UUID,
        query: str,
        limit: int | None = None,
        score_threshold: float | None = None,
    ):
        dataset = await self.get_by_id(dataset_id)

        if not dataset.is_vectorized:
            raise NotFoundException("Dataset is not vectorized yet")

        self.__ensure_dataset_embedding_is_compatible(dataset)

        if await self.vector_store_service.count_documents(dataset.id) == 0:
            raise NotFoundException(
                "Vector index not found. Please vectorize dataset again."
            )

        query_embedding = self.embedding_service.embed_text(query)

        effective_limit = (
            self.default_k_retrieval
            if limit is None
            else limit
        )

        effective_score_threshold = (
            self.default_score_threshold
            if score_threshold is None
            else score_threshold
        )

        self.__validate_score_threshold(
            effective_score_threshold
        )

        return await self.vector_store_service.similarity_search(
            dataset_id=dataset.id,
            query_embedding=query_embedding,
            limit=effective_limit,
            score_threshold=(
                effective_score_threshold
            ),
        )

    def __validate_dataset_ownership(
        self,
        scope: DatasetScope,
        owner_user_id: UUID | None,
    ) -> None:
        if scope == DatasetScope.ADMIN and owner_user_id is not None:
            raise BadRequestException(
                "Admin datasets must not have an owner_user_id."
            )

        if scope == DatasetScope.USER and owner_user_id is None:
            raise BadRequestException(
                "User datasets must have an owner_user_id."
            )

    def __ensure_dataset_embedding_is_compatible(
        self,
        dataset: Dataset,
    ) -> None:
        if (
            dataset.embedding_provider is None
            or dataset.embedding_model is None
            or dataset.embedding_dimension is None
        ):
            raise BadRequestException(
                "Dataset embedding metadata is missing. "
                "Please vectorize this dataset again with the active embedding provider."
            )

        if dataset.embedding_provider != self.embedding_service.provider_name:
            raise BadRequestException(
                f"Dataset was vectorized with embedding provider "
                f"'{dataset.embedding_provider}', but active provider is "
                f"'{self.embedding_service.provider_name}'. "
                f"Please vectorize this dataset again."
            )

        if dataset.embedding_model != self.embedding_service.model_name:
            raise BadRequestException(
                f"Dataset was vectorized with embedding model "
                f"'{dataset.embedding_model}', but active model is "
                f"'{self.embedding_service.model_name}'. "
                f"Please vectorize this dataset again."
            )

        if dataset.embedding_dimension != self.embedding_service.dimension:
            raise BadRequestException(
                f"Dataset was vectorized with dimension "
                f"{dataset.embedding_dimension}, but active embedding dimension is "
                f"{self.embedding_service.dimension}. "
                f"Please vectorize this dataset again."
            )

    def __validate_score_threshold(
        self,
        score_threshold: float | None,
    ) -> None:
        if score_threshold is None:
            return

        if score_threshold < 0 or score_threshold > 1:
            raise BadRequestException(
                "score_threshold must be between 0 and 1."
            )

    async def __build_chunks(
        self,
        dataset_id: UUID,
    ):
        dataset = await self.get_by_id(
            dataset_id
        )

        storage_file_name = (
            dataset.storage_file_name
            or dataset.file_name
        )

        if not self.file_storage_service.exists(
            storage_file_name
        ):
            raise NotFoundException(
                "Dataset file not found"
            )

        file_path = (
            self.file_storage_service.get_file_path(
                storage_file_name
            )
        )

        return self.document_processing_service.process_file(
            dataset_id=dataset.id,
            file_path=file_path,
        )
