from dependency_injector import containers, providers

from src.application.application_collection import ApplicationCollection
from src.application.web import WebService


def run_app(web_service: WebService) -> None:
    web_service.start()


class WebHostCollection(containers.DeclarativeContainer):
    main = providers.Callable(
        run_app,
        web_service=ApplicationCollection.web_service,
    )
