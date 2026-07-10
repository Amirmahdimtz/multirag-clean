from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.dataset import Dataset


class IDatasetRepository(ABC):
    @abstractmethod
    async def add(self, dataset: Dataset) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[Dataset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Dataset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_scope(self, scope: DatasetScope) -> List[Dataset]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_owner_user_id(self, owner_user_id: UUID) -> List[Dataset]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, dataset: Dataset) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, dataset: Dataset) -> None:
        raise NotImplementedError
