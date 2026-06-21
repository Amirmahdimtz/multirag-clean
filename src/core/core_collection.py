from dependency_injector import containers, providers

from src.core.user.user_business import UserBusiness
from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.core.dataset.dataset_business import DatasetBusiness
from src.infrastructure.infrastructure_collection import InfrastructureCollection


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
    )
