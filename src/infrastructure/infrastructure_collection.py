from dependency_injector import containers, providers

from src.infrastructure.config.config_reader import ConfigReader


class InfrastructureCollection(containers.DeclarativeContainer):
    config_reader = providers.Singleton(ConfigReader)
