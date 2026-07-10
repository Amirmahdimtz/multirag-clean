from typing import List
from uuid import UUID

from src.core.contracts.repositories.i_rag_access_repository import IRAGAccessRepository
from src.core.contracts.repositories.i_rag_system_repository import IRAGSystemRepository
from src.core.contracts.repositories.i_user_repository import IUserRepository
from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.models.rag_access import RAGAccess
from src.domain.models.rag_system import RAGSystem
from src.domain.models.user import User


class RAGAccessBusiness:
    def __init__(
        self,
        rag_access_repository: IRAGAccessRepository,
        user_repository: IUserRepository,
        rag_system_repository: IRAGSystemRepository,
    ) -> None:
        self.rag_access_repository = rag_access_repository
        self.user_repository = user_repository
        self.rag_system_repository = rag_system_repository

    async def grant_access(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> RAGAccess:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise NotFoundException("User not found")

        rag_system = await self.rag_system_repository.get_by_id(rag_system_id)

        if rag_system is None:
            raise NotFoundException("RAG system not found")

        access_exists = await self.rag_access_repository.exists(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        if access_exists:
            raise BadRequestException(
                "User already has access to this RAG system"
            )

        rag_access = RAGAccess(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        return await self.rag_access_repository.add(rag_access)

    async def revoke_access(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise NotFoundException("User not found")

        rag_system = await self.rag_system_repository.get_by_id(rag_system_id)

        if rag_system is None:
            raise NotFoundException("RAG system not found")

        removed = await self.rag_access_repository.remove_by_user_and_rag_system(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        if not removed:
            raise NotFoundException("RAG access not found")

    async def has_access(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> bool:
        return await self.rag_access_repository.exists(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

    async def ensure_user_has_access(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> None:
        access_exists = await self.has_access(
            user_id=user_id,
            rag_system_id=rag_system_id,
        )

        if not access_exists:
            raise ForbiddenException(
                "User does not have access to this RAG system"
            )

    async def get_users_by_rag_system(
        self,
        rag_system_id: UUID,
    ) -> List[User]:
        rag_system = await self.rag_system_repository.get_by_id(rag_system_id)

        if rag_system is None:
            raise NotFoundException("RAG system not found")

        return await self.rag_access_repository.get_users_by_rag_system_id(
            rag_system_id=rag_system_id,
        )

    async def get_rag_systems_by_user(
        self,
        user_id: UUID,
    ) -> List[RAGSystem]:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise NotFoundException("User not found")

        return await self.rag_access_repository.get_rag_systems_by_user_id(
            user_id=user_id,
        )
