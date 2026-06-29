from dependency_injector import containers, providers

from src.core.user.user_business import UserBusiness
from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.core.dataset.dataset_business import DatasetBusiness
from src.core.rag_system.rag_system_business import RAGSystemBusiness


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

    rag_system_business = providers.Factory(
        RAGSystemBusiness,
        rag_system_repository=InfrastructureCollection.rag_system_repository,
        dataset_repository=InfrastructureCollection.dataset_repository,
        embedding_service=InfrastructureCollection.embedding_service,
        vector_store_service=InfrastructureCollection.vector_store_service,
    )
