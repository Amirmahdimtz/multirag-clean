from dependency_injector import containers, providers

from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.core.user.user_business import UserBusiness


class CoreCollection(containers.DeclarativeContainer):
    user_business = providers.Factory(
        UserBusiness,
        user_repository=InfrastructureCollection.user_repository,
    )
