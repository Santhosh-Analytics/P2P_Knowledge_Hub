from uuid import UUID
from pydantic import BaseModel


class GenerationContext(BaseModel):
    answer: str
    citations: list[GenerationCitation]
