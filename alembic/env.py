import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.models.chat_message import ChatMessage  # noqa: F401
from src.domain.models.chat_session import ChatSession  # noqa: F401
from src.domain.models.dataset import Dataset  # noqa: F401
from src.domain.models.rag_access import RAGAccess  # noqa: F401
from src.domain.models.rag_system import RAGSystem  # noqa: F401
from src.domain.models.user import User  # noqa: F401
from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.base import Base
from src.infrastructure.vector_store.vector_document_record import (
    VectorDocumentRecord,  # noqa: F401
)


target_metadata = Base.metadata


def get_database_url() -> str:
    return str(
        ConfigReader().require(
            "database.url",
        )
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=(
            connection.dialect.name == "sqlite"
        ),
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(
                do_run_migrations
            )
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(
        run_async_migrations()
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
