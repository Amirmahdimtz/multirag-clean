from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID, uuid4


@dataclass
class VectorDocument:
    dataset_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: Dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
