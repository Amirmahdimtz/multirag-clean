from fastapi import UploadFile
from pydantic import BaseModel


class UploadDatasetRequestDto(BaseModel):
    name: str
