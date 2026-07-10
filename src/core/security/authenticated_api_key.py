from dataclasses import dataclass
from uuid import UUID

from src.domain.enums.api_key_role import ApiKeyRole


@dataclass(frozen=True)
class AuthenticatedApiKey:
    role: ApiKeyRole
    api_key: str
    user_id: UUID | None = None
