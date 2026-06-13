from pathlib import Path
from typing import Any

import yaml


class ConfigReader:
    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self.__load_config()

    def __load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def get(self, key: str, default: Any = None) -> Any:
        value = self.config

        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default

            value = value[part]

        return value
