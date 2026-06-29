from dataclasses import dataclass


@dataclass
class RAGAnswerContextResult:
    chunk_index: int
    content: str
    score: float
