from enum import Enum


class LLMType(str, Enum):
    SIMPLE = "simple"
    RAG = "rag"
    USER_RAG = "user_rag"
