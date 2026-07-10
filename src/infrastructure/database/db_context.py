from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy import make_url, text

from src.infrastructure.database.base import Base


class DbContext:
    def __init__(
        self,
        database_url: str,
        echo_sql: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        pool_recycle_seconds: int = 1800,
    ) -> None:
        engine_options = {
            "echo": echo_sql,
            "future": True,
        }

        if make_url(database_url).get_backend_name() == "postgresql":
            engine_options.update(
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=pool_pre_ping,
                pool_recycle=pool_recycle_seconds,
            )

        self.engine = create_async_engine(
            database_url,
            **engine_options,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        from src.domain.models.user import User  # noqa: F401
        from src.domain.models.dataset import Dataset  # noqa: F401
        from src.domain.models.rag_system import RAGSystem  # noqa: F401
        from src.domain.models.rag_access import RAGAccess  # noqa: F401
        from src.domain.models.chat_session import ChatSession  # noqa: F401
        from src.domain.models.chat_message import ChatMessage  # noqa: F401
        from src.infrastructure.vector_store.vector_document_record import (  # noqa: F401
            VectorDocumentRecord,
        )

        async with self.engine.begin() as conn:

            await self._enable_pgvector(conn)

            await conn.run_sync(
                Base.metadata.create_all
            )

    async def _enable_pgvector(self, conn) -> None:
        """
        Enable pgvector extension only for PostgreSQL.
        SQLite does not support this extension.
        """

        if self.engine.dialect.name == "postgresql":
            await conn.execute(
                text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                )
            )

    def get_session(self) -> AsyncSession:
        return self.session_factory()
