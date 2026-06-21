from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.common.base_entity import BaseEntity


class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
