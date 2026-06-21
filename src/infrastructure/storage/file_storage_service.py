from pathlib import Path
import uuid
from fastapi import UploadFile


class FileStorageService:
    def __init__(self, base_path: str = "storage") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    async def save_file(self, file: UploadFile) -> str:
        file_extension = Path(file.filename).suffix
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = self.base_path / file_name

        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        return file_name

    def get_file_path(self, file_name: str) -> str:
        return str(self.base_path / file_name)
