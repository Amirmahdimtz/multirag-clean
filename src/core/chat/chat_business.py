from typing import AsyncGenerator, List
from uuid import UUID

from src.core.chat.chat_history_service import ChatHistoryService
from src.core.chat.chat_message_business import ChatMessageBusiness
from src.core.chat.chat_session_business import ChatSessionBusiness
from src.core.dataset.user_dataset_business import UserDatasetBusiness
from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.forbidden_exception import ForbiddenException
from src.core.llm.llm_factory import LLMFactory
from src.core.rag_access.rag_access_business import RAGAccessBusiness
from src.core.rag_system.rag_system_business import RAGSystemBusiness
from src.domain.enums.llm_type import LLMType
from src.domain.models.chat_session import ChatSession
from src.domain.models.vector_search_result import VectorSearchResult


class ChatBusiness:
    def __init__(
        self,
        chat_session_business: ChatSessionBusiness,
        chat_message_business: ChatMessageBusiness,
        rag_system_business: RAGSystemBusiness,
        rag_access_business: RAGAccessBusiness,
        user_dataset_business: UserDatasetBusiness,
        llm_factory: LLMFactory,
        chat_history_service: ChatHistoryService,
    ) -> None:
        self.chat_session_business = chat_session_business
        self.chat_message_business = chat_message_business
        self.rag_system_business = rag_system_business
        self.rag_access_business = rag_access_business
        self.user_dataset_business = user_dataset_business
        self.llm_factory = llm_factory
        self.chat_history_service = chat_history_service

    async def create_session(
        self,
        user_id: UUID,
        name: str,
        llm_type: str = "simple",
        rag_system_id: UUID | None = None,
        user_dataset_id: UUID | None = None,
    ) -> ChatSession:
        parsed_llm_type = self.__parse_llm_type(llm_type)

        await self.__validate_session_resources(
            user_id=user_id,
            llm_type=parsed_llm_type,
            rag_system_id=rag_system_id,
            user_dataset_id=user_dataset_id,
        )

        return await self.chat_session_business.create_session(
            user_id=user_id,
            name=name,
            llm_type=parsed_llm_type,
            rag_system_id=rag_system_id,
            user_dataset_id=user_dataset_id,
        )

    async def get_user_sessions(
        self,
        user_id: UUID,
    ) -> List[ChatSession]:
        return await self.chat_session_business.get_user_sessions(
            user_id=user_id,
        )

    async def get_session_owner_id(
        self,
        session_id: UUID,
    ) -> UUID:
        session = await self.chat_session_business.get_by_id(
            session_id
        )

        return session.user_id

    async def get_session_messages(
        self,
        session_id: UUID,
    ):
        return await self.chat_message_business.get_session_messages(
            session_id=session_id,
        )

    async def delete_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> None:
        session = await self.chat_session_business.get_by_id(
            session_id
        )

        if session.user_id != user_id:
            raise ForbiddenException(
                "You are not allowed to delete this chat session"
            )

        await self.chat_message_business.delete_session_messages(
            session_id
        )

        await self.chat_session_business.delete_session(
            session_id
        )

    async def ensure_user_can_use_rag_system(
        self,
        session_id: UUID,
        rag_system_id: UUID | None = None,
    ) -> None:
        session = await self.chat_session_business.get_by_id(
            session_id
        )

        if session.llm_type != LLMType.RAG:
            if rag_system_id is not None:
                raise BadRequestException(
                    "rag_system_id can only be used "
                    "with RAG chat sessions."
                )

            return

        effective_rag_system_id = (
            rag_system_id
            or session.rag_system_id
        )

        if effective_rag_system_id is None:
            raise BadRequestException(
                "rag_system_id is required "
                "for RAG chat sessions."
            )

        await self.rag_access_business.ensure_user_has_access(
            user_id=session.user_id,
            rag_system_id=effective_rag_system_id,
        )

    async def ensure_user_can_use_user_dataset(
        self,
        session_id: UUID,
        user_dataset_id: UUID | None = None,
    ) -> None:
        session = await self.chat_session_business.get_by_id(
            session_id
        )

        if session.llm_type != LLMType.USER_RAG:
            if user_dataset_id is not None:
                raise BadRequestException(
                    "user_dataset_id can only be used "
                    "with USER_RAG chat sessions."
                )

            return

        effective_user_dataset_id = (
            user_dataset_id
            or session.user_dataset_id
        )

        if effective_user_dataset_id is None:
            raise BadRequestException(
                "user_dataset_id is required "
                "for USER_RAG chat sessions."
            )

        await self.user_dataset_business.ensure_user_owns_dataset(
            user_id=session.user_id,
            dataset_id=effective_user_dataset_id,
        )

    async def stream_message(
        self,
        session_id: UUID,
        question: str,
        rag_system_id: UUID | None = None,
        user_dataset_id: UUID | None = None,
    ) -> AsyncGenerator[str, None]:
        session = await self.chat_session_business.get_by_id(
            session_id
        )

        history_messages = (
            await self.chat_message_business
            .get_session_messages(
                session_id=session_id,
            )
        )

        history_text = (
            self.chat_history_service
            .build_history_text(
                history_messages,
            )
        )

        llm, contexts = (
            await self.__resolve_llm_and_contexts(
                session=session,
                question=question,
                rag_system_id=rag_system_id,
                user_dataset_id=user_dataset_id,
            )
        )

        await self.chat_message_business.add_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        full_question = f"""
CHAT HISTORY:
{history_text}

CURRENT QUESTION:
{question}
""".strip()

        full_response = ""

        async for token in llm.stream(
            question=full_question,
            contexts=contexts,
        ):
            full_response += token

            yield token

        await self.chat_message_business.add_message(
            session_id=session_id,
            role="assistant",
            content=full_response,
        )

        await self.chat_session_business.update_last_active(
            session_id
        )

    async def __resolve_llm_and_contexts(
        self,
        session: ChatSession,
        question: str,
        rag_system_id: UUID | None = None,
        user_dataset_id: UUID | None = None,
    ):
        if session.llm_type == LLMType.SIMPLE:
            self.__ensure_no_rag_resources_for_simple_session(
                session=session,
                rag_system_id=rag_system_id,
                user_dataset_id=user_dataset_id,
            )

            return (
                self.llm_factory.create_simple_llm(),
                [],
            )

        if session.llm_type == LLMType.RAG:
            effective_rag_system_id = (
                rag_system_id
                or session.rag_system_id
            )

            if effective_rag_system_id is None:
                raise BadRequestException(
                    "rag_system_id is required "
                    "for RAG chat sessions."
                )

            if (
                user_dataset_id is not None
                or session.user_dataset_id is not None
            ):
                raise BadRequestException(
                    "USER_RAG datasets cannot be used "
                    "with RAG chat sessions."
                )

            await (
                self.rag_access_business
                .ensure_user_has_access(
                    user_id=session.user_id,
                    rag_system_id=(
                        effective_rag_system_id
                    ),
                )
            )

            rag_results = (
                await self.rag_system_business.search(
                    rag_system_id=(
                        effective_rag_system_id
                    ),
                    query=question,
                )
            )

            return (
                self.llm_factory.create_rag_llm(),
                self.__build_llm_contexts(
                    rag_results
                ),
            )

        if session.llm_type == LLMType.USER_RAG:
            effective_user_dataset_id = (
                user_dataset_id
                or session.user_dataset_id
            )

            if effective_user_dataset_id is None:
                raise BadRequestException(
                    "user_dataset_id is required "
                    "for USER_RAG chat sessions."
                )

            if (
                rag_system_id is not None
                or session.rag_system_id is not None
            ):
                raise BadRequestException(
                    "rag_system_id cannot be used "
                    "with USER_RAG chat sessions."
                )

            user_rag_results = (
                await self.user_dataset_business
                .search_user_dataset(
                    user_id=session.user_id,
                    dataset_id=(
                        effective_user_dataset_id
                    ),
                    query=question,
                )
            )

            return (
                self.llm_factory.create_user_rag_llm(),
                self.__build_llm_contexts(
                    user_rag_results
                ),
            )

        raise BadRequestException(
            "Unsupported llm_type."
        )

    async def __validate_session_resources(
        self,
        user_id: UUID,
        llm_type: LLMType,
        rag_system_id: UUID | None,
        user_dataset_id: UUID | None,
    ) -> None:
        if llm_type == LLMType.SIMPLE:
            if (
                rag_system_id is not None
                or user_dataset_id is not None
            ):
                raise BadRequestException(
                    "SIMPLE chat sessions must not "
                    "have rag_system_id or "
                    "user_dataset_id."
                )

            return

        if llm_type == LLMType.RAG:
            if rag_system_id is None:
                raise BadRequestException(
                    "rag_system_id is required "
                    "for RAG chat sessions."
                )

            if user_dataset_id is not None:
                raise BadRequestException(
                    "user_dataset_id cannot be used "
                    "with RAG chat sessions."
                )

            await (
                self.rag_access_business
                .ensure_user_has_access(
                    user_id=user_id,
                    rag_system_id=rag_system_id,
                )
            )

            return

        if llm_type == LLMType.USER_RAG:
            if user_dataset_id is None:
                raise BadRequestException(
                    "user_dataset_id is required "
                    "for USER_RAG chat sessions."
                )

            if rag_system_id is not None:
                raise BadRequestException(
                    "rag_system_id cannot be used "
                    "with USER_RAG chat sessions."
                )

            await (
                self.user_dataset_business
                .ensure_user_owns_dataset(
                    user_id=user_id,
                    dataset_id=user_dataset_id,
                )
            )

            return

        raise BadRequestException(
            "Unsupported llm_type."
        )

    def __ensure_no_rag_resources_for_simple_session(
        self,
        session: ChatSession,
        rag_system_id: UUID | None,
        user_dataset_id: UUID | None,
    ) -> None:
        if (
            rag_system_id is not None
            or user_dataset_id is not None
            or session.rag_system_id is not None
            or session.user_dataset_id is not None
        ):
            raise BadRequestException(
                "SIMPLE chat sessions cannot "
                "use RAG resources."
            )

    def __parse_llm_type(
        self,
        llm_type: str,
    ) -> LLMType:
        try:
            return LLMType(llm_type)

        except ValueError as exc:
            raise BadRequestException(
                f"Unsupported llm_type "
                f"'{llm_type}'."
            ) from exc

    def __build_llm_contexts(
        self,
        search_results: List[
            VectorSearchResult
        ],
    ) -> List[str]:
        contexts: List[str] = []

        for result in search_results:
            document_content = (
                result.document.content
            )

            metadata = (
                result.document.metadata
                or {}
            )

            answer = str(
                metadata.get(
                    "answer",
                    "",
                )
                or ""
            ).strip()

            if answer:
                document_content = f"""
Question:
{document_content}

Answer:
{answer}
""".strip()

            context = f"""
[chunk: {result.document.chunk_index}]
{document_content}
""".strip()

            contexts.append(
                context
            )

        return contexts
