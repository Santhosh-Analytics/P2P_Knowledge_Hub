from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    Department,
    MimeType,
    SourceDocumentKey,
    DocumentStatus,
    SourceSystem,
)


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    document_group_id: UUID
    document_name: str
    document_status: DocumentStatus
    document_version: int
    source_system: SourceSystem
    business_process: BusinessProcess
    uploaded_at: datetime
    uploaded_by: str
    department: Department
    source_uri: str
    file_hash: str
    file_size_bytes: int
    mime_type: MimeType
    source_document_key: SourceDocumentKey
    chunks_length: int
