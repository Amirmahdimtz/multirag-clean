from pydantic import BaseModel


class DocumentChunkPreviewDto(BaseModel):
    chunk_index: int
    content: str
    character_count: int
