from dependency_injector import containers, providers

from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.dataset_repository import DatasetRepository
from src.infrastructure.repositories.chat_session_repository import ChatSessionRepository
from src.infrastructure.repositories.chat_message_repository import ChatMessageRepository
from src.infrastructure.repositories.rag_system_repository import RAGSystemRepository
from src.infrastructure.storage.file_storage_service import FileStorageService
from src.infrastructure.document_processing.text_extractor import TextExtractor
from src.infrastructure.document_processing.text_splitter import TextSplitter
from src.infrastructure.embedding.embedding_service import EmbeddingService
from src.infrastructure.vector_store.in_memory_vector_store_service import (
    InMemoryVectorStoreService,
)
from src.infrastructure.document_processing.document_processing_service import (
    DocumentProcessingService,
)


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

    text_extractor = providers.Singleton(
        TextExtractor,
    )

    text_splitter = providers.Singleton(
        TextSplitter,
        chunk_size=1000,
        chunk_overlap=150,
    )

    document_processing_service = providers.Singleton(
        DocumentProcessingService,
        text_extractor=text_extractor,
        text_splitter=text_splitter,
    )

    embedding_service = providers.Singleton(
        EmbeddingService,
        dimension=128,
    )

    vector_store_service = providers.Singleton(
        InMemoryVectorStoreService,
    )
