from pydantic import BaseModel


class UploadDatasetRequestDto(BaseModel):
    name: str
