import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.config.config_reader import ConfigReader


class ConfigReaderTests(unittest.TestCase):
    def test_resolves_environment_values_and_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.yaml"
            config_path.write_text(
                """
application:
  port: "${MULTIRAG_TEST_PORT:8000}"
  enabled: "${MULTIRAG_TEST_ENABLED:true}"
  values: '${MULTIRAG_TEST_VALUES:["default"]}'
  optional: "${MULTIRAG_TEST_OPTIONAL:null}"
""".strip(),
                encoding="utf-8",
            )

            previous_cwd = Path.cwd()
            os.chdir(temp_path)

            try:
                with patch.dict(
                    os.environ,
                    {
                        "MULTIRAG_TEST_PORT": "9000",
                        "MULTIRAG_TEST_ENABLED": "false",
                        "MULTIRAG_TEST_VALUES": '["one","two"]',
                    },
                    clear=False,
                ):
                    reader = ConfigReader(str(config_path))
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(9000, reader.require("application.port"))
        self.assertFalse(reader.require("application.enabled"))
        self.assertEqual(
            ["one", "two"],
            reader.require("application.values"),
        )
        self.assertIsNone(reader.get("application.optional"))

    def test_require_raises_for_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                "application:\n  name: MultiRAG\n",
                encoding="utf-8",
            )
            reader = ConfigReader(str(config_path))

        with self.assertRaises(KeyError):
            reader.require("application.port")


if __name__ == "__main__":
    unittest.main()
