from enum import Enum


class DatasetScope(str, Enum):
    ADMIN = "admin"
    USER = "user"
