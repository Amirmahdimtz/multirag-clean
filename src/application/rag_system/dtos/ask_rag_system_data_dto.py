from typing import List

from pydantic import BaseModel

from src.application.rag_system.dtos.rag_answer_context_dto import (
    RAGAnswerContextDto,
)


class AskRAGSystemDataDto(BaseModel):
    answer: str
    contexts: List[RAGAnswerContextDto]
