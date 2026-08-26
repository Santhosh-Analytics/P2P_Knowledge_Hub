from pydantic import model_validator
from p2p_knowledge_hub.models.retrieved_chunk import RetrievalSource
from pydantic import BaseModel, Field
from typing import Self


class QueryRequest(BaseModel):
    query: str
    retriever: RetrievalSource
    candidate_k: int = Field(default=20, ge=1)
    top_k: int = Field(default=3, ge=1)

    @model_validator(mode="after")
    def validate_k(self) -> Self:
        if self.top_k > self.candidate_k:
            raise ValueError("top_k cannot be greater than candidate_k")

        return self
