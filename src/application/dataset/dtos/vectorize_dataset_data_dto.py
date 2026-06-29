from pydantic import BaseModel


class VectorizeDatasetDataDto(BaseModel):
    vector_count: int
