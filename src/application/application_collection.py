from dependency_injector import containers, providers

from src.application.health.health_controller import HealthController
from src.application.web import WebService
from src.infrastructure.infrastructure_collection import InfrastructureCollection


class ApplicationCollection(containers.DeclarativeContainer):
    health_controller = providers.Factory(
        HealthController,
        config_reader=InfrastructureCollection.config_reader,
    )

    controllers = providers.List(
        health_controller,
    )

    web_service = providers.Factory(
        WebService,
        config_reader=InfrastructureCollection.config_reader,
        controllers=controllers,
    )
