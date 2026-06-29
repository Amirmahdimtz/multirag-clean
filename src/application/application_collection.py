from dependency_injector import containers, providers

from src.application.web import WebService
from src.core.core_collection import CoreCollection
from src.application.user.user_controller import UserController
from src.application.health.health_controller import HealthController
from src.application.dataset.dataset_controller import DatasetController
from src.application.chat.chat_controller import ChatController
from src.infrastructure.infrastructure_collection import InfrastructureCollection
from src.application.rag_system.rag_system_controller import (
    RAGSystemController,
)


class ApplicationCollection(containers.DeclarativeContainer):

    health_controller = providers.Factory(
        HealthController,
        config_reader=InfrastructureCollection.config_reader,
    )

    user_controller = providers.Factory(
        UserController,
        user_business=CoreCollection.user_business,
    )

    dataset_controller = providers.Factory(
        DatasetController,
        dataset_business=CoreCollection.dataset_business,
    )

    rag_system_controller = providers.Factory(
        RAGSystemController,
        rag_system_business=CoreCollection.rag_system_business,
    )

    chat_controller = providers.Factory(
        ChatController,
        chat_business=CoreCollection.chat_business,
    )

    controllers = providers.List(
        health_controller,
        user_controller,
        dataset_controller,
        rag_system_controller,
        chat_controller,
    )

    web_service = providers.Factory(
        WebService,
        config_reader=InfrastructureCollection.config_reader,
        controllers=controllers,
        db_context=InfrastructureCollection.db_context,
    )
