from uuid import UUID
from pydantic import BaseModel


class GenerationCitation(BaseModel):
    source_id: int
    chunk_id: UUID
    document_name: str
    page_no: int | None = None
    section: str | None = None
    title: str | None = None
    source_uri: str
