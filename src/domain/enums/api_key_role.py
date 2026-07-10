from enum import Enum


class ApiKeyRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
