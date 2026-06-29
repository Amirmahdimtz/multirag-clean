from pydantic import BaseModel, Field


class AskRAGSystemRequestDto(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=20)
