import json
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.core.chat.chat_business import ChatBusiness
from src.core.security.authenticated_api_key import AuthenticatedApiKey


class CreateChatSessionInput(BaseModel):
    user_id: UUID
    name: str
    llm_type: str = "simple"
    rag_system_id: UUID | None = None
    user_dataset_id: UUID | None = None


class ChatHistoryInput(BaseModel):
    user_id: UUID
    session_id: UUID


class DeleteChatSessionInput(BaseModel):
    user_id: UUID
    session_id: UUID


class ChatInput(BaseModel):
    user_id: UUID
    session_id: UUID
    user_prompt: str
    llm_type: str = "simple"
    rag_system_id: UUID | None = None
    user_dataset_id: UUID | None = None


class ChatController(BaseController):
    route_prefix = "/user/chat"

    def __init__(
        self,
        chat_business: ChatBusiness,
        api_key_dependencies: ApiKeyDependencies,
    ) -> None:
        self.chat_business = chat_business
        self.api_key_dependencies = api_key_dependencies

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["Chat"],
            responses={404: {"description": "Not found"}},
        )

        @router.post("/create")
        async def create_session_main_compatible(
            data: CreateChatSessionInput = Body(),
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_or_admin_api_key
            ),
        ):
            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=data.user_id,
            )

            session = await self.chat_business.create_session(
                user_id=data.user_id,
                name=data.name,
                llm_type=data.llm_type,
                rag_system_id=data.rag_system_id,
                user_dataset_id=data.user_dataset_id,
            )

            return self.__session_response(session)

        @router.get("")
        async def get_user_sessions_main_compatible(
            user_id: UUID,
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_or_admin_api_key
            ),
        ):
            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=user_id,
            )

            sessions = await self.chat_business.get_user_sessions(
                user_id=user_id,
            )

            return self.__sessions_response(sessions)

        @router.post("/history")
        async def get_chat_history(
            user_id: UUID,
            session_id: UUID,
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_or_admin_api_key
            ),
        ):
            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=user_id,
            )

            session_owner_id = await self.chat_business.get_session_owner_id(
                session_id=session_id,
            )

            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=session_owner_id,
            )

            messages = await self.chat_business.get_session_messages(
                session_id=session_id,
            )

            return BaseResponseDto(
                success=True,
                message="Chat history fetched successfully",
                data=[
                    {
                        "id": message.id,
                        "session_id": message.session_id,
                        "role": message.role.value,
                        "content": message.content,
                        "created_at": message.created_at,
                    }
                    for message in messages
                ],
            )

        @router.delete("")
        async def delete_chat_session(
            user_id: UUID,
            session_id: UUID,
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_or_admin_api_key
            ),
        ):
            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=user_id,
            )

            await self.chat_business.delete_session(
                user_id=user_id,
                session_id=session_id,
            )

            return BaseResponseDto(
                success=True,
                message="Chat session deleted successfully",
                data=None,
            )

        @router.post("")
        async def chat_main_compatible(
            data: ChatInput = Body(),
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_or_admin_api_key
            ),
        ):
            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=data.user_id,
            )

            session_owner_id = await self.chat_business.get_session_owner_id(
                session_id=data.session_id,
            )

            self.api_key_dependencies.require_same_user_or_admin(
                authenticated_api_key=authenticated_api_key,
                user_id=session_owner_id,
            )

            await self.chat_business.ensure_user_can_use_rag_system(
                session_id=data.session_id,
                rag_system_id=data.rag_system_id,
            )

            await self.chat_business.ensure_user_can_use_user_dataset(
                session_id=data.session_id,
                user_dataset_id=data.user_dataset_id,
            )

            async def event_generator():
                index = 0
                completion = ""

                async for token in self.chat_business.stream_message(
                    session_id=data.session_id,
                    question=data.user_prompt,
                    rag_system_id=data.rag_system_id,
                    user_dataset_id=data.user_dataset_id,
                ):
                    index += 1
                    completion += token

                    yield json.dumps(
                        {
                            "token": token,
                            "index": index,
                            "completion": completion,
                        },
                        ensure_ascii=False,
                    ) + "\n"

            return StreamingResponse(
                event_generator(),
                media_type="application/x-ndjson; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                },
            )

        return router

    def __session_response(self, session):
        return BaseResponseDto(
            success=True,
            message="Chat session created successfully",
            data={
                "id": session.id,
                "user_id": session.user_id,
                "name": session.name,
                "llm_type": session.llm_type.value,
                "rag_system_id": session.rag_system_id,
                "user_dataset_id": session.user_dataset_id,
                "last_active_at": session.last_active_at,
            },
        )

    def __sessions_response(self, sessions):
        return BaseResponseDto(
            success=True,
            message="Chat sessions fetched successfully",
            data=[
                {
                    "id": session.id,
                    "user_id": session.user_id,
                    "name": session.name,
                    "llm_type": session.llm_type.value,
                    "rag_system_id": session.rag_system_id,
                    "user_dataset_id": session.user_dataset_id,
                    "last_active_at": session.last_active_at,
                }
                for session in sessions
            ],
        )
