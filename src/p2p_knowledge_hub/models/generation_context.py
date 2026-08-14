from uuid import UUID
from pydantic import BaseModel


class GenerationContext(BaseModel):
    chunk_id: UUID
    text: str
    document_name: str
    page_no: int | None = None
    section: str | None = None
    title: str | None = None
    source_uri: str
