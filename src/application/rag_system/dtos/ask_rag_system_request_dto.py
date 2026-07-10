from pydantic import BaseModel, Field


class AskRAGSystemRequestDto(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
    )

    limit: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    score_threshold: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
