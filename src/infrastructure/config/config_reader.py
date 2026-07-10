import json
import os
import re
from pathlib import Path
from typing import Any

import yaml


class ConfigReader:
    __ENV_PATTERN = re.compile(
        r"^\$\{([A-Za-z_][A-Za-z0-9_]*)(?::(.*))?\}$"
    )

    def __init__(self, config_path: str = "config/config.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self.__load_config()

    def __load_config(self) -> dict:
        self.__load_env_file()

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}"
            )

        with self.config_path.open("r", encoding="utf-8") as file:
            raw_config = yaml.safe_load(file) or {}

        return self.__resolve_env_values(raw_config)

    def __load_env_file(self) -> None:
        env_path = Path(".env")

        if not env_path.exists():
            return

        with env_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if (
                    len(value) >= 2
                    and value[0] == value[-1]
                    and value[0] in {"'", '"'}
                ):
                    value = value[1:-1]

                os.environ.setdefault(key, value)

    def __resolve_env_values(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self.__resolve_env_values(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self.__resolve_env_values(item)
                for item in value
            ]

        if not isinstance(value, str):
            return value

        match = self.__ENV_PATTERN.match(value)

        if match is None:
            return value

        env_name = match.group(1)
        default_value = match.group(2)

        env_value = os.getenv(env_name, default_value)

        if env_value is None:
            return None

        return self.__parse_env_value(env_value)

    def __parse_env_value(self, value: str) -> Any:
        value = value.strip()

        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        if value.lower() in {"none", "null"}:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def get(self, key: str, default: Any = None) -> Any:
        value = self.config

        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default

            value = value[part]

        return value

    def require(self, key: str) -> Any:
        value = self.config

        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                raise KeyError(f"Required config key not found: {key}")

            value = value[part]

        if value is None:
            raise ValueError(f"Required config key has no value: {key}")

        return value
