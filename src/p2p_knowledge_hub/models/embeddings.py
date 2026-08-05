from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from enum import StrEnum

from p2p_knowledge_hub.models.document import tz_aware_time


class DocumentEmbedding(BaseModel):
    chunk_id: UUID
    embeddings: list[float]
    embedding_provider: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=tz_aware_time)
    embedding_dimension: int
