from src.domain.models.dataset import Dataset
from src.domain.enums.dataset_type import DatasetType


class DatasetBusiness:
    def __init__(self, dataset_repository, file_storage_service) -> None:
        self.dataset_repository = dataset_repository
        self.file_storage_service = file_storage_service

    async def upload_dataset(self, name: str, file) -> Dataset:
        file_name = await self.file_storage_service.save_file(file)

        dataset = Dataset(
            name=name,
            file_name=file_name,
            dataset_type=DatasetType.UNKNOWN,
            is_vectorized=False,
        )

        return await self.dataset_repository.add(dataset)

    async def get_all(self):
        return await self.dataset_repository.get_all()

    async def get_by_id(self, dataset_id):
        return await self.dataset_repository.get_by_id(Dataset, dataset_id)

    async def delete(self, dataset):
        return await self.dataset_repository.delete(dataset)
