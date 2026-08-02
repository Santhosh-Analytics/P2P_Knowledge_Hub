from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class DocumentPage(BaseModel):
    document_id: UUID
    document_group_id: UUID
    text: str | None = None
    page_no: int | None = None
    section: str | None = None
    title: str | None = None


class DocumentChunk(BaseModel):
    chunk_id: UUID
    chunk_index: int
    chunking_version: int = 1
    document_id: UUID
    document_group_id: UUID
    is_active: bool
    created_at: datetime = datetime.now()
    text: str | None = None
    page_no: int | None = None
    section: str | None = None
    title: str | None = None
