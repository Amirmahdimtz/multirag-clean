import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.dataset.user_dataset_business import UserDatasetBusiness
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.domain.enums.dataset_scope import DatasetScope


class UserDatasetBusinessTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_dataset_owned_by_user(self) -> None:
        user_id = uuid4()
        dataset_id = uuid4()
        dataset = SimpleNamespace(
            id=dataset_id,
            scope=DatasetScope.USER,
            owner_user_id=user_id,
        )

        dataset_business = SimpleNamespace(
            get_by_id=AsyncMock(return_value=dataset),
        )
        business = UserDatasetBusiness(dataset_business=dataset_business)

        result = await business.get_owned_user_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
        )

        self.assertIs(dataset, result)
        dataset_business.get_by_id.assert_awaited_once_with(dataset_id)

    async def test_rejects_access_to_another_users_dataset(self) -> None:
        user_id = uuid4()
        dataset_id = uuid4()
        dataset = SimpleNamespace(
            id=dataset_id,
            scope=DatasetScope.USER,
            owner_user_id=uuid4(),
        )

        dataset_business = SimpleNamespace(
            get_by_id=AsyncMock(return_value=dataset),
        )
        business = UserDatasetBusiness(dataset_business=dataset_business)

        with self.assertRaises(ForbiddenException):
            await business.get_owned_user_dataset(
                user_id=user_id,
                dataset_id=dataset_id,
            )

    async def test_rejects_admin_dataset_as_user_owned(self) -> None:
        user_id = uuid4()
        dataset_id = uuid4()
        dataset = SimpleNamespace(
            id=dataset_id,
            scope=DatasetScope.ADMIN,
            owner_user_id=None,
        )

        dataset_business = SimpleNamespace(
            get_by_id=AsyncMock(return_value=dataset),
        )
        business = UserDatasetBusiness(dataset_business=dataset_business)

        with self.assertRaises(ForbiddenException):
            await business.get_owned_user_dataset(
                user_id=user_id,
                dataset_id=dataset_id,
            )


if __name__ == "__main__":
    unittest.main()
