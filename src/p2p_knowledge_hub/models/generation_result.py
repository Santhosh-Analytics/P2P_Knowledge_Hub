from p2p_knowledge_hub.models.generation_citation import GenerationCitation
from pydantic import BaseModel


class GenerationResult(BaseModel):
    answer: str
    citations: list[GenerationCitation]
