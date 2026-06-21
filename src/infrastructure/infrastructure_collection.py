from dependency_injector import containers, providers

from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.dataset_repository import DatasetRepository
from src.infrastructure.repositories.chat_session_repository import ChatSessionRepository
from src.infrastructure.repositories.chat_message_repository import ChatMessageRepository
from src.infrastructure.repositories.rag_system_repository import RAGSystemRepository
from src.infrastructure.storage.file_storage_service import FileStorageService


class InfrastructureCollection(containers.DeclarativeContainer):
    config_reader = providers.Singleton(ConfigReader)

    db_context = providers.Singleton(
        DbContext,
        database_url=config_reader.provided.get.call(
            "database.url",
            "sqlite+aiosqlite:///./test.db",
        ),
    )

    user_repository = providers.Factory(
        UserRepository,
        db_context=db_context,
    )

    dataset_repository = providers.Factory(
        DatasetRepository,
        db_context=db_context,
    )

    chat_session_repository = providers.Factory(
        ChatSessionRepository,
        db_context=db_context,
    )

    chat_message_repository = providers.Factory(
        ChatMessageRepository,
        db_context=db_context,
    )

    rag_system_repository = providers.Factory(
        RAGSystemRepository,
        db_context=db_context,
    )

    file_storage_service = providers.Singleton(
        FileStorageService,
    )
