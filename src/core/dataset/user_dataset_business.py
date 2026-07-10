from uuid import UUID

from src.core.dataset.dataset_business import DatasetBusiness
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.dataset import Dataset


class UserDatasetBusiness:
    def __init__(
        self,
        dataset_business: DatasetBusiness,
    ) -> None:
        self.dataset_business = dataset_business

    async def upload_user_dataset(
        self,
        user_id: UUID,
        name: str,
        file,
    ) -> Dataset:
        return await self.dataset_business.upload_dataset(
            name=name,
            file=file,
            scope=DatasetScope.USER,
            owner_user_id=user_id,
        )

    async def get_user_datasets(
        self,
        user_id: UUID,
    ) -> list[Dataset]:
        return await self.dataset_business.get_by_owner_user_id(
            owner_user_id=user_id,
        )

    async def vectorize_user_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
    ) -> int:
        await self.get_owned_user_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
        )

        return await self.dataset_business.vectorize_dataset(
            dataset_id=dataset_id,
        )

    async def search_user_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
        query: str,
        limit: int | None = None,
        score_threshold: float | None = None,
    ):
        await self.get_owned_user_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
        )

        return await self.dataset_business.search_dataset(
            dataset_id=dataset_id,
            query=query,
            limit=limit,
            score_threshold=score_threshold,
        )

    async def delete_user_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
    ) -> None:
        dataset = await self.get_owned_user_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
        )

        await self.dataset_business.delete(dataset)

    async def ensure_user_owns_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
    ) -> None:
        await self.get_owned_user_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
        )

    async def get_owned_user_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
    ) -> Dataset:
        dataset = await self.dataset_business.get_by_id(dataset_id)

        if (
            dataset.scope != DatasetScope.USER
            or dataset.owner_user_id != user_id
        ):
            raise ForbiddenException(
                "You are not allowed to access another user's dataset"
            )

        return dataset
