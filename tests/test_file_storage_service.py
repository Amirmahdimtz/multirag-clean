import tempfile
import unittest
from pathlib import Path

from src.infrastructure.storage.file_storage_service import FileStorageService


class FileStorageServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_save_content_persists_bytes_with_original_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = FileStorageService(base_path=temp_dir)

            stored_name = await service.save_content(
                file_name="example.txt",
                content=b"hello",
            )

            self.assertTrue(stored_name.endswith(".txt"))
            stored_path = Path(service.get_file_path(stored_name))
            self.assertTrue(stored_path.exists())
            self.assertEqual(b"hello", stored_path.read_bytes())

    async def test_save_content_generates_unique_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = FileStorageService(base_path=temp_dir)

            first = await service.save_content("same.txt", b"one")
            second = await service.save_content("same.txt", b"two")

            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
