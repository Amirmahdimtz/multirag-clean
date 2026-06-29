from uuid import UUID

from fastapi import APIRouter

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.core.chat.chat_business import ChatBusiness


class ChatController(BaseController):
    route_prefix = "/chat"

    def __init__(self, chat_business: ChatBusiness) -> None:
        self.chat_business = chat_business

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["Chat"],
        )

        @router.post("/sessions")
        async def create_session(
            user_id: UUID,
            name: str,
            llm_type: str = "simple",
        ):
            session = await self.chat_business.create_session(
                user_id=user_id,
                name=name,
                llm_type=llm_type,
            )

            return BaseResponseDto(
                success=True,
                message="Chat session created successfully",
                data={
                    "id": session.id,
                    "user_id": session.user_id,
                    "name": session.name,
                    "llm_type": session.llm_type.value,
                },
            )

        @router.get("/users/{user_id}/sessions")
        async def get_user_sessions(user_id: UUID):
            sessions = await self.chat_business.get_user_sessions(
                user_id=user_id,
            )

            return BaseResponseDto(
                success=True,
                message="Chat sessions fetched successfully",
                data=[
                    {
                        "id": session.id,
                        "user_id": session.user_id,
                        "name": session.name,
                        "llm_type": session.llm_type.value,
                        "is_active": session.is_active,
                    }
                    for session in sessions
                ],
            )

        @router.post("/send")
        async def send_message(
            session_id: UUID,
            question: str,
            rag_system_id: UUID | None = None,
        ):
            answer = await self.chat_business.send_message(
                session_id=session_id,
                question=question,
                rag_system_id=rag_system_id,
            )

            return BaseResponseDto(
                success=True,
                message="Message processed successfully",
                data={
                    "answer": answer,
                },
            )

        return router
