import unittest
from uuid import UUID, uuid4

from src.core.exceptions.forbidden_exception import ForbiddenException
from src.core.exceptions.unauthorized_exception import UnauthorizedException
from src.core.security.api_key_auth_service import ApiKeyAuthService
from src.core.security.authenticated_api_key import AuthenticatedApiKey
from src.domain.enums.api_key_role import ApiKeyRole


class ApiKeyAuthServiceTests(unittest.TestCase):
    def test_disabled_security_returns_admin_identity(self) -> None:
        service = ApiKeyAuthService(enabled=False)

        authenticated = service.authenticate(api_key=None)

        self.assertEqual(ApiKeyRole.ADMIN, authenticated.role)
        self.assertIsNone(authenticated.user_id)

    def test_admin_key_authenticates_as_admin(self) -> None:
        service = ApiKeyAuthService(
            enabled=True,
            admin_api_keys=["admin-secret"],
        )

        authenticated = service.authenticate(api_key="admin-secret")

        self.assertEqual(ApiKeyRole.ADMIN, authenticated.role)
        self.assertIsNone(authenticated.user_id)

    def test_user_key_is_bound_to_configured_user(self) -> None:
        user_id = uuid4()
        service = ApiKeyAuthService(
            enabled=True,
            user_api_keys=[
                {
                    "api_key": "user-secret",
                    "user_id": str(user_id),
                }
            ],
        )

        authenticated = service.authenticate(api_key="user-secret")

        self.assertEqual(ApiKeyRole.USER, authenticated.role)
        self.assertEqual(user_id, authenticated.user_id)

    def test_invalid_key_is_rejected(self) -> None:
        service = ApiKeyAuthService(
            enabled=True,
            admin_api_keys=["admin-secret"],
        )

        with self.assertRaises(UnauthorizedException):
            service.authenticate(api_key="wrong-key")

    def test_user_cannot_access_another_users_resource(self) -> None:
        authenticated = AuthenticatedApiKey(
            role=ApiKeyRole.USER,
            api_key="user-secret",
            user_id=UUID("11111111-1111-1111-1111-111111111111"),
        )
        service = ApiKeyAuthService(enabled=True)

        with self.assertRaises(ForbiddenException):
            service.require_same_user_or_admin(
                authenticated_api_key=authenticated,
                user_id=UUID("22222222-2222-2222-2222-222222222222"),
            )


if __name__ == "__main__":
    unittest.main()
