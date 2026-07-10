from secrets import compare_digest
from typing import Sequence
from uuid import UUID

from src.core.exceptions.forbidden_exception import ForbiddenException
from src.core.exceptions.unauthorized_exception import UnauthorizedException
from src.core.security.authenticated_api_key import AuthenticatedApiKey
from src.domain.enums.api_key_role import ApiKeyRole


class ApiKeyAuthService:
    def __init__(
        self,
        enabled: bool,
        admin_api_keys: Sequence[str] | None = None,
        user_api_keys: Sequence[dict] | None = None,
    ) -> None:
        self.enabled = enabled
        self.admin_api_keys = self.__normalize_admin_keys(admin_api_keys)
        self.user_api_keys = self.__normalize_user_keys(user_api_keys)

    def authenticate(
        self,
        api_key: str | None,
    ) -> AuthenticatedApiKey:
        if not self.enabled:
            return AuthenticatedApiKey(
                role=ApiKeyRole.ADMIN,
                api_key="auth-disabled",
                user_id=None,
            )

        if not api_key:
            raise UnauthorizedException("API key is required")

        if self.__matches_any_admin_key(api_key):
            return AuthenticatedApiKey(
                role=ApiKeyRole.ADMIN,
                api_key=api_key,
                user_id=None,
            )

        matched_user_key = self.__find_user_key(api_key)

        if matched_user_key is not None:
            return AuthenticatedApiKey(
                role=ApiKeyRole.USER,
                api_key=api_key,
                user_id=matched_user_key["user_id"],
            )

        raise UnauthorizedException("Invalid API key")

    def require_admin(
        self,
        authenticated_api_key: AuthenticatedApiKey,
    ) -> None:
        if authenticated_api_key.role != ApiKeyRole.ADMIN:
            raise ForbiddenException("Admin API key is required")

    def require_user(
        self,
        authenticated_api_key: AuthenticatedApiKey,
    ) -> None:
        if authenticated_api_key.role != ApiKeyRole.USER:
            raise ForbiddenException("User API key is required")

        if authenticated_api_key.user_id is None:
            raise ForbiddenException("User API key must be bound to a user")

    def require_user_or_admin(
        self,
        authenticated_api_key: AuthenticatedApiKey,
    ) -> None:
        if authenticated_api_key.role not in {
            ApiKeyRole.ADMIN,
            ApiKeyRole.USER,
        }:
            raise ForbiddenException("User or admin API key is required")

    def require_same_user_or_admin(
        self,
        authenticated_api_key: AuthenticatedApiKey,
        user_id: UUID,
    ) -> None:
        if authenticated_api_key.role == ApiKeyRole.ADMIN:
            return

        if (
            authenticated_api_key.role == ApiKeyRole.USER
            and authenticated_api_key.user_id == user_id
        ):
            return

        raise ForbiddenException(
            "You are not allowed to access another user's resource"
        )

    def __matches_any_admin_key(
        self,
        provided_key: str,
    ) -> bool:
        return any(
            compare_digest(provided_key, valid_key)
            for valid_key in self.admin_api_keys
        )

    def __find_user_key(
        self,
        provided_key: str,
    ) -> dict | None:
        for item in self.user_api_keys:
            if compare_digest(provided_key, item["api_key"]):
                return item

        return None

    def __normalize_admin_keys(
        self,
        keys: Sequence[str] | None,
    ) -> list[str]:
        if keys is None:
            return []

        return [
            key.strip()
            for key in keys
            if isinstance(key, str) and key.strip()
        ]

    def __normalize_user_keys(
        self,
        keys: Sequence[dict] | None,
    ) -> list[dict]:
        if keys is None:
            return []

        normalized_keys = []

        for item in keys:
            if not isinstance(item, dict):
                continue

            api_key = str(item.get("api_key", "")).strip()
            user_id_value = str(item.get("user_id", "")).strip()

            if not api_key or not user_id_value:
                continue

            normalized_keys.append(
                {
                    "api_key": api_key,
                    "user_id": UUID(user_id_value),
                }
            )

        return normalized_keys
