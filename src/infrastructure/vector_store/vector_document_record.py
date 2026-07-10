from uuid import uuid4

from sqlalchemy import Column, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class VectorDocumentRecord(Base):
    __tablename__ = "vector_documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    dataset_id: Mapped[str] = mapped_column(
        String(36),
        index=True,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding = Column(
        JSON,
        nullable=False,
    )

    metadata_json = Column(
        JSON,
        nullable=True,
    )
