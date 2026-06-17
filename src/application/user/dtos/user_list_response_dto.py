from typing import List
from src.application.user.dtos.user_response_dto import UserResponseDto
from src.application.common.dtos.base_response_dto import BaseResponseDto


class UserListResponseDto(BaseResponseDto):
    data: List[UserResponseDto]
