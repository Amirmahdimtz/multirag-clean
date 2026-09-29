import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config


class MigrationTests(unittest.TestCase):
    def test_upgrade_head_matches_metadata_and_downgrade_removes_schema(
        self,
    ) -> None:
        expected_tables = {
            "users",
            "datasets",
            "rag_systems",
            "rag_accesses",
            "chat_sessions",
            "chat_messages",
            "vector_documents",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = (
                Path(temp_dir)
                / "migration.db"
            )

            database_url = (
                "sqlite+aiosqlite:///"
                f"{database_path.as_posix()}"
            )

            alembic_config = Config(
                "alembic.ini"
            )

            with patch.dict(
                os.environ,
                {
                    "MULTIRAG_DATABASE_URL": (
                        database_url
                    ),
                },
                clear=False,
            ):
                command.upgrade(
                    alembic_config,
                    "head",
                )

                command.check(
                    alembic_config
                )

                with sqlite3.connect(
                    database_path
                ) as connection:
                    tables = {
                        row[0]
                        for row in connection.execute(
                            """
                            SELECT name
                            FROM sqlite_master
                            WHERE type = 'table'
                            """
                        )
                    }

                self.assertTrue(
                    expected_tables
                    .issubset(tables)
                )

                command.downgrade(
                    alembic_config,
                    "base",
                )

                with sqlite3.connect(
                    database_path
                ) as connection:
                    tables_after_downgrade = {
                        row[0]
                        for row in connection.execute(
                            """
                            SELECT name
                            FROM sqlite_master
                            WHERE type = 'table'
                            """
                        )
                    }

                self.assertFalse(
                    expected_tables
                    & tables_after_downgrade
                )


if __name__ == "__main__":
    unittest.main()
