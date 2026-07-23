from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID, uuid4


def tz_aware_time() -> datetime:
    return datetime.now(timezone.utc)


class SourceSystem(str, Enum):
    SAP = "SAP"
    ORACLE = "ORACLE"
    TALLY = "TALLY"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Department(str, Enum):
    CONTRACT = "CONTRACT"
    VMF = "VMF"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    INVOICE = "INVOICE"
    PAYMENT = "PAYMENT"


class BusinessProcess(str, Enum):
    SUPPLIER = "SUPPLIER"
    INVOICE = "INVOICE"
    PURCHASEORDER = "PURCHASEORDER"
    PAYMENT = "PAYMENT"


class MimeType(str, Enum):
    PDF = "application/pdf"


class Document(BaseModel):
    document_id: UUID = Field(default_factory=uuid4, frozen=True)
    document_group_id: UUID
    document_name: str
    document_status: DocumentStatus = DocumentStatus.UPLOADED
    document_version: int = Field(default=1, ge=1)
    source_system: SourceSystem
    business_process: BusinessProcess
    uploaded_at: datetime = Field(default_factory=tz_aware_time)
    uploaded_by: str
    department: Department
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
    data = Document()
    data.document_id = uuid4()
    print(data)
    print(data.model_dump())
    print(data.model_dump_json(indent=2))
