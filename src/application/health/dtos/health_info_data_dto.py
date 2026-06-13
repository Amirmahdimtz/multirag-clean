from pydantic import BaseModel


class HealthInfoDataDto(BaseModel):
    project: str
    architecture: str
    python_version: str
