from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass
class DocumentChunk:
    dataset_id: UUID
    content: str
    chunk_index: int
    token_count: Optional[int] = None
    metadata: dict = field(default_factory=dict)
