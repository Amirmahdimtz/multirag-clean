from pydantic import BaseModel


class RAGAnswerContextDto(BaseModel):
    chunk_index: int
    content: str
    score: float
