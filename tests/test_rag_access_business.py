import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.core.rag_access.rag_access_business import RAGAccessBusiness


class RAGAccessBusinessTests(unittest.IsolatedAsyncioTestCase):
    def build_business(
        self,
        *,
        access_exists: bool = False,
        user_exists: bool = True,
        rag_system_exists: bool = True,
    ):
        user_id = uuid4()
        rag_system_id = uuid4()

        user_repository = SimpleNamespace(
            get_by_id=AsyncMock(
                return_value=(
                    SimpleNamespace(id=user_id)
                    if user_exists
                    else None
                )
            )
        )
        rag_system_repository = SimpleNamespace(
            get_by_id=AsyncMock(
                return_value=(
                    SimpleNamespace(id=rag_system_id)
                    if rag_system_exists
                    else None
                )
            )
        )
        rag_access_repository = SimpleNamespace(
            exists=AsyncMock(return_value=access_exists),
            add=AsyncMock(side_effect=lambda entity: entity),
        )

        business = RAGAccessBusiness(
            rag_access_repository=rag_access_repository,
            user_repository=user_repository,
            rag_system_repository=rag_system_repository,
        )

        return (
            business,
            rag_access_repository,
            user_id,
            rag_system_id,
        )

    async def test_grant_access_creates_binding(self) -> None:
        (
            business,
            rag_access_repository,
            user_id,
            rag_system_id,
        ) = self.build_business()

        result = await business.grant_access(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        self.assertEqual(user_id, result.user_id)
        self.assertEqual(rag_system_id, result.rag_system_id)
        rag_access_repository.add.assert_awaited_once()

    async def test_grant_access_rejects_duplicate_binding(self) -> None:
        (
            business,
            _,
            user_id,
            rag_system_id,
        ) = self.build_business(access_exists=True)

        with self.assertRaises(BadRequestException):
            await business.grant_access(
                user_id=user_id,
                rag_system_id=rag_system_id,
            )

    async def test_missing_access_is_forbidden(self) -> None:
        (
            business,
            _,
            user_id,
            rag_system_id,
        ) = self.build_business(access_exists=False)

        with self.assertRaises(ForbiddenException):
            await business.ensure_user_has_access(
                user_id=user_id,
                rag_system_id=rag_system_id,
            )


if __name__ == "__main__":
    unittest.main()
