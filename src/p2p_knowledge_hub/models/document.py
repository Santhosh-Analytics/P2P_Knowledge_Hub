from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID, uuid4


def tz_aware_time() -> datetime:
    return datetime.now(timezone.utc)


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class MimeType(str, Enum):
    PDF = "application/pdf"


class Document(BaseModel):
    document_id: UUID = Field(default_factory=uuid4, frozen=True)
    document_name: str
    document_type: str | None = None
    document_status: DocumentStatus = DocumentStatus.UPLOADED
    document_version: int = Field(default=1, ge=1)
    uploaded_at: datetime = Field(default_factory=tz_aware_time)
    uploaded_by: str
    department: str
    source_uri: str
    file_hash: str = Field(min_length=64, max_length=64)
    file_size_bytes: int = Field(gt=0)
    mime_type: MimeType = MimeType.PDF

    model_config = ConfigDict(
        frozen=True,
        str_min_length=1,
        extra="forbid",
    )


if __name__ == "__main__":
    data = Document(
        document_name="test",
        document_type="test_type",
        # document_version=1,
        # document_version="2",
        uploaded_by="test_uploadedby",
        department="p2p",
        source_uri="source_uri",
        file_hash="a" * 64,
        file_size_bytes=32,
    )
    print(data)
    print(data.model_dump())
    print(data.model_dump_json(indent=2))
