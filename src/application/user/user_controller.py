from fastapi import APIRouter

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.user.dtos.create_user_request_dto import (
    CreateUserRequestDto,
)
from src.core.user.user_business import UserBusiness
from src.application.user.dtos.user_response_dto import UserResponseDto


class UserController(BaseController):
    route_prefix = "/users"

    def __init__(self, user_business: UserBusiness) -> None:
        self.user_business = user_business

    def api(self) -> APIRouter:
        router = APIRouter(
            tags=["Users"],
        )

        @router.post("/")
        async def create_user(
            dto: CreateUserRequestDto,
        ) -> BaseResponseDto:
            user = await self.user_business.create_user(
                dto.username,
            )

            return BaseResponseDto(
                success=True,
                message="User created",
                data=UserResponseDto(
                    id=user.id,
                    username=user.username,
                ),
            )

        @router.get("/")
        async def get_users() -> BaseResponseDto:
            users = await self.user_business.get_all_users()

            return BaseResponseDto(
                success=True,
                message="Users fetched",
                data=[
                    UserResponseDto(
                        id=user.id,
                        username=user.username,
                    )
                    for user in users
                ],
            )

        return router
