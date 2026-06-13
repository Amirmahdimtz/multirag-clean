from pydantic import BaseModel


class HealthDataDto(BaseModel):
    status: str
    application_name: str
    version: str
