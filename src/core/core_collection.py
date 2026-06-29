from dependency_injector import containers, providers

from src.core.user.user_business import UserBusiness
from src.core.chat.chat_history_service import ChatHistoryService
from src.core.chat.chat_session_business import ChatSessionBusiness
from src.core.chat.chat_message_business import ChatMessageBusiness
from src.core.chat.chat_business import ChatBusiness
from src.core.chat.chat_llm import ChatLLM
from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.core.dataset.dataset_business import DatasetBusiness
from src.core.rag_system.rag_system_business import RAGSystemBusiness
from src.core.llm.llm_factory import LLMFactory


class CoreCollection(containers.DeclarativeContainer):
    user_business = providers.Factory(
        UserBusiness,
        user_repository=InfrastructureCollection.user_repository,
    )

    dataset_business = providers.Factory(
        DatasetBusiness,
        dataset_repository=InfrastructureCollection.dataset_repository,
        file_storage_service=InfrastructureCollection.file_storage_service,
        document_processing_service=InfrastructureCollection.document_processing_service,
        embedding_service=InfrastructureCollection.embedding_service,
        vector_store_service=InfrastructureCollection.vector_store_service,
    )

    llm_factory = providers.Factory(
        LLMFactory,
        chat_model_service=InfrastructureCollection.chat_model_service,
    )

    chat_session_business = providers.Factory(
        ChatSessionBusiness,
        chat_session_repository=InfrastructureCollection.chat_session_repository,
    )

    chat_message_business = providers.Factory(
        ChatMessageBusiness,
        chat_message_repository=InfrastructureCollection.chat_message_repository,
    )

    chat_history_service = providers.Singleton(
        ChatHistoryService,
    )

    chat_llm = providers.Factory(
        ChatLLM,
        llm_factory=llm_factory,
        chat_history_service=chat_history_service,
    )

    rag_system_business = providers.Factory(
        RAGSystemBusiness,
        rag_system_repository=InfrastructureCollection.rag_system_repository,
        dataset_repository=InfrastructureCollection.dataset_repository,
        embedding_service=InfrastructureCollection.embedding_service,
        vector_store_service=InfrastructureCollection.vector_store_service,
        llm_factory=llm_factory,
    )

    chat_business = providers.Factory(
        ChatBusiness,
        chat_session_business=chat_session_business,
        chat_message_business=chat_message_business,
        rag_system_business=rag_system_business,
        chat_llm=chat_llm,
    )
