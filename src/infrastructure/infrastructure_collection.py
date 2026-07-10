from dependency_injector import containers, providers

from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.db_context import DbContext

from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.dataset_repository import DatasetRepository
from src.infrastructure.repositories.chat_session_repository import ChatSessionRepository
from src.infrastructure.repositories.chat_message_repository import ChatMessageRepository
from src.infrastructure.repositories.rag_system_repository import RAGSystemRepository
from src.infrastructure.repositories.rag_access_repository import RAGAccessRepository

from src.infrastructure.storage.file_storage_service import FileStorageService

from src.infrastructure.document_processing.text_extractor import TextExtractor
from src.infrastructure.document_processing.text_splitter import TextSplitter

from src.infrastructure.embedding.embedding_service import EmbeddingService

from src.infrastructure.llm.fake_chat_model_service import FakeChatModelService

from src.infrastructure.embedding.jina_embedding_service import JinaEmbeddingService
from src.infrastructure.llm.vllm_chat_model_service import VLLMChatModelService


from src.infrastructure.document_processing.document_processing_service import (
    DocumentProcessingService,
)
from src.infrastructure.vector_store.persistent_vector_store_service import (
    PersistentVectorStoreService,
)
from src.infrastructure.vector_store.pgvector_store_service import (
    PGVectorStoreService,
)


class InfrastructureCollection(containers.DeclarativeContainer):
    config_reader = providers.Singleton(ConfigReader)

    db_context = providers.Singleton(
        DbContext,
        database_url=config_reader.provided.require.call("database.url"),
        echo_sql=config_reader.provided.require.call("database.echo_sql"),
        pool_size=config_reader.provided.require.call("database.pool_size"),
        max_overflow=config_reader.provided.require.call(
            "database.max_overflow"
        ),
        pool_pre_ping=config_reader.provided.require.call(
            "database.pool_pre_ping"
        ),
        pool_recycle_seconds=config_reader.provided.require.call(
            "database.pool_recycle_seconds"
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

    rag_access_repository = providers.Factory(
        RAGAccessRepository,
        db_context=db_context,
    )
    file_storage_service = providers.Singleton(
        FileStorageService,
        base_path=config_reader.provided.require.call("storage.base_path"),
    )

    text_extractor = providers.Singleton(
        TextExtractor,
    )

    text_splitter = providers.Singleton(
        TextSplitter,
        chunk_size=config_reader.provided.require.call(
            "document_processing.chunk_size",
        ),
        chunk_overlap=config_reader.provided.require.call(
            "document_processing.chunk_overlap",
        ),
    )

    document_processing_service = providers.Singleton(
        DocumentProcessingService,
        text_extractor=text_extractor,
        text_splitter=text_splitter,
    )

    fake_embedding_service = providers.Singleton(
        EmbeddingService,
        dimension=config_reader.provided.require.call("embedding.dimension"),
    )

    jina_embedding_service = providers.Singleton(
        JinaEmbeddingService,
        model_name=config_reader.provided.require.call(
            "embedding.jina.model_name"),
        vector_size=config_reader.provided.require.call(
            "embedding.jina.vector_size"),
        offline=config_reader.provided.require.call("embedding.jina.offline"),
        local_model_path=config_reader.provided.get.call(
            "embedding.jina.local_model_path",
            None,
        ),
        normalize_embeddings=config_reader.provided.require.call(
            "embedding.jina.normalize_embeddings",
        ),
        device=config_reader.provided.require.call("embedding.jina.device"),
    )

    embedding_service = providers.Selector(
        config_reader.provided.require.call("embedding.provider"),
        fake=fake_embedding_service,
        jina=jina_embedding_service,
    )

    persistent_vector_store_service = providers.Singleton(
        PersistentVectorStoreService,
        db_context=db_context,
    )

    pgvector_store_service = providers.Singleton(
        PGVectorStoreService,

        db_context=db_context,

        embedding_service=(
            embedding_service
        ),

        table_prefix=(
            config_reader
            .provided
            .require
            .call(
                "vector_store.pgvector.table_prefix"
            )
        ),

        vector_size=(
            config_reader
            .provided
            .require
            .call(
                "vector_store.pgvector.vector_size"
            )
        ),

        batch_size=(
            config_reader
            .provided
            .require
            .call(
                "vector_store.pgvector.batch_size"
            )
        ),

        hnsw_enabled=(
            config_reader
            .provided
            .get
            .call(
                "vector_store.pgvector.hnsw.enabled",
                True,
            )
        ),
    )

    vector_store_service = providers.Selector(
        config_reader.provided.require.call("vector_store.provider"),
        sqlite_json=persistent_vector_store_service,
        pgvector=pgvector_store_service,
    )

    fake_chat_model_service = providers.Singleton(
        FakeChatModelService,
    )

    vllm_chat_model_service = providers.Singleton(
        VLLMChatModelService,
        model=config_reader.provided.require.call("llm.vllm.model"),
        base_url=config_reader.provided.require.call("llm.vllm.base_url"),
        api_key=config_reader.provided.require.call("llm.vllm.api_key"),
        temperature=config_reader.provided.require.call(
            "llm.vllm.temperature"
        ),
        max_tokens=config_reader.provided.require.call(
            "llm.vllm.max_tokens"
        ),
        top_p=config_reader.provided.require.call("llm.vllm.top_p"),
        top_k=config_reader.provided.require.call("llm.vllm.top_k"),
        timeout_seconds=config_reader.provided.require.call(
            "llm.vllm.timeout_seconds"
        ),
    )

    chat_model_service = providers.Selector(
        config_reader.provided.require.call("llm.provider"),
        fake=fake_chat_model_service,
        vllm=vllm_chat_model_service,
    )
