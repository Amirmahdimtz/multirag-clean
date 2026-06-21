from uuid import UUID

from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.enums.dataset_type import DatasetType
from src.domain.models.dataset import Dataset


class DatasetBusiness:
    def __init__(
        self,
        dataset_repository,
        file_storage_service,
        document_processing_service,
    ) -> None:
        self.dataset_repository = dataset_repository
        self.file_storage_service = file_storage_service
        self.document_processing_service = document_processing_service

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
        return await self.dataset_repository.delete(dataset)

    async def preview_chunks(self, dataset_id: UUID, limit: int = 5):
        dataset = await self.get_by_id(dataset_id)

        if not self.file_storage_service.exists(dataset.file_name):
            raise NotFoundException("Dataset file not found")

        file_path = self.file_storage_service.get_file_path(dataset.file_name)

        chunks = self.document_processing_service.process_file(
            dataset_id=dataset.id,
            file_path=file_path,
        )

        return chunks[:limit]
