from pydantic import BaseModel


class VectorSearchResultDto(BaseModel):
    chunk_index: int
    content: str
    score: float
