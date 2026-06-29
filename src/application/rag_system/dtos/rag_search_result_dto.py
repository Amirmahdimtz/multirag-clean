from pydantic import BaseModel


class RAGSearchResultDto(BaseModel):
    chunk_index: int
    content: str
    score: float
