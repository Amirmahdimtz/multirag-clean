from dependency_injector import containers, providers

from src.application.web import WebService
from src.core.core_collection import CoreCollection
from src.application.user.user_controller import UserController
from src.application.health.health_controller import HealthController
from src.application.dataset.dataset_controller import DatasetController
from src.application.dataset.user_dataset_controller import UserDatasetController
from src.application.chat.chat_controller import ChatController
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.application.rag_access.rag_access_controller import RAGAccessController
from src.application.rag_system.rag_system_controller import (
    RAGSystemController,
)


class ApplicationCollection(containers.DeclarativeContainer):

    api_key_dependencies = providers.Factory(
        ApiKeyDependencies,
        api_key_auth_service=CoreCollection.api_key_auth_service,
    )

    health_controller = providers.Factory(
        HealthController,
        config_reader=InfrastructureCollection.config_reader,
    )

    user_controller = providers.Factory(
        UserController,
        user_business=CoreCollection.user_business,
        api_key_dependencies=api_key_dependencies,
    )

    dataset_controller = providers.Factory(
        DatasetController,
        dataset_business=CoreCollection.dataset_business,
        api_key_dependencies=api_key_dependencies,
    )

    user_dataset_controller = providers.Factory(
        UserDatasetController,
        user_dataset_business=CoreCollection.user_dataset_business,
        api_key_dependencies=api_key_dependencies,
    )

    rag_system_controller = providers.Factory(
        RAGSystemController,
        rag_system_business=CoreCollection.rag_system_business,
        api_key_dependencies=api_key_dependencies,
    )

    rag_access_controller = providers.Factory(
        RAGAccessController,
        rag_access_business=CoreCollection.rag_access_business,
        api_key_dependencies=api_key_dependencies,
    )

    chat_controller = providers.Factory(
        ChatController,
        chat_business=CoreCollection.chat_business,
        api_key_dependencies=api_key_dependencies,
    )

    controllers = providers.List(
        health_controller,
        user_controller,
        dataset_controller,
        user_dataset_controller,
        rag_system_controller,
        rag_access_controller,
        chat_controller,
    )

    web_service = providers.Factory(
        WebService,
        config_reader=InfrastructureCollection.config_reader,
        controllers=controllers,
        db_context=InfrastructureCollection.db_context,
    )
