from uuid import UUID

from fastapi import Header

from src.core.exceptions.unauthorized_exception import UnauthorizedException
from src.core.security.api_key_auth_service import ApiKeyAuthService
from src.core.security.authenticated_api_key import AuthenticatedApiKey


class ApiKeyDependencies:
    def __init__(
        self,
        api_key_auth_service: ApiKeyAuthService,
    ) -> None:
        self.api_key_auth_service = api_key_auth_service

    async def require_admin_api_key(
        self,
        authorization: str | None = Header(
            default=None,
            alias="Authorization",
        ),
    ) -> AuthenticatedApiKey:
        authenticated_api_key = self.__authenticate_authorization_header(
            authorization=authorization,
        )

        self.api_key_auth_service.require_admin(
            authenticated_api_key=authenticated_api_key,
        )

        return authenticated_api_key

    async def require_user_api_key(
        self,
        authorization: str | None = Header(
            default=None,
            alias="Authorization",
        ),
    ) -> AuthenticatedApiKey:
        authenticated_api_key = self.__authenticate_authorization_header(
            authorization=authorization,
        )

        self.api_key_auth_service.require_user(
            authenticated_api_key=authenticated_api_key,
        )

        return authenticated_api_key

    async def require_user_or_admin_api_key(
        self,
        authorization: str | None = Header(
            default=None,
            alias="Authorization",
        ),
    ) -> AuthenticatedApiKey:
        authenticated_api_key = self.__authenticate_authorization_header(
            authorization=authorization,
        )

        self.api_key_auth_service.require_user_or_admin(
            authenticated_api_key=authenticated_api_key,
        )

        return authenticated_api_key

    def require_same_user_or_admin(
        self,
        authenticated_api_key: AuthenticatedApiKey,
        user_id: UUID,
    ) -> None:
        self.api_key_auth_service.require_same_user_or_admin(
            authenticated_api_key=authenticated_api_key,
            user_id=user_id,
        )

    def __authenticate_authorization_header(
        self,
        authorization: str | None,
    ) -> AuthenticatedApiKey:
        if not self.api_key_auth_service.enabled:
            return self.api_key_auth_service.authenticate(
                api_key=None,
            )

        api_key = self.__extract_bearer_token(
            authorization=authorization,
        )

        return self.api_key_auth_service.authenticate(
            api_key=api_key,
        )

    def __extract_bearer_token(
        self,
        authorization: str | None,
    ) -> str:
        if authorization is None or not authorization.strip():
            raise UnauthorizedException(
                "Authorization header is required"
            )

        scheme, separator, token = authorization.strip().partition(" ")

        if not separator:
            raise UnauthorizedException(
                "Invalid authorization header format"
            )

        if scheme.lower() != "bearer":
            raise UnauthorizedException(
                "Invalid authorization header format"
            )

        token = token.strip()

        if not token:
            raise UnauthorizedException(
                "API key is required"
            )

        return token
