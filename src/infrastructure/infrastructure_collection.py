from dependency_injector import containers, providers

from src.infrastructure.config.config_reader import ConfigReader
from src.infrastructure.database.db_context import DbContext


class InfrastructureCollection(containers.DeclarativeContainer):
    config_reader = providers.Singleton(ConfigReader)

    db_context = providers.Singleton(
        DbContext,
        database_url=config_reader.provided.get.call("database.url"),
    )
