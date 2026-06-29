from dataclasses import dataclass
from typing import List

from src.core.rag_system.rag_answer_context_result import (
    RAGAnswerContextResult,
)


@dataclass
class RAGAnswerResult:
    answer: str
    contexts: List[RAGAnswerContextResult]
