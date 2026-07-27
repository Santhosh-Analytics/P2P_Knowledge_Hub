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
    SAP_ARIBA = "SAP_ARIBA"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Department(str, Enum):
    PROCUREMENT = "PROCUREMENT"
    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"
    FINANCE = "FINANCE"
    SUPPLIER_MANAGEMENT = "SUPPLIER_MANAGEMENT"


class SourceDocumentKey(str, Enum):
    PROCUREMENT_POLICY = "PROCUREMENT_POLICY"
    CONTRACTING_POLICY = "CONTRACTING_POLICY"
    SUPPLIER_ONBOARDING_POLICY = "SUPPLIER_ONBOARDING_POLICY"
    SINGLE_PAYMENT_REQUEST_POLICY = "SINGLE_PAYMENT_REQUEST_POLICY"
    INVOICE_POLICY = "INVOICE_POLICY"
    PAYMENT_POLICY = "PAYMENT_POLICY"
    PURCHASING_POLICY = "PURCHASING_POLICY"
    SUPPLIER_ONBOARDING_SOP = "SUPPLIER_ONBOARDING_SOP"
    SINGLE_PAYMENT_REQUEST_SOP = "SINGLE_PAYMENT_REQUEST_SOP"
    INVOICE_APPROVAL_SOP = "INVOICE_APPROVAL_SOP"
    PAYMENT_SOP = "PAYMENT_SOP"
    PURCHASE_ORDER_SOP = "PURCHASE_ORDER_SOP"


class BusinessProcess(str, Enum):
    CONTRACT = "CONTRACT"
    SOURCING = "SOURCING"
    SUPPLIER_ONBOARDING = "SUPPLIER_ONBOARDING"
    SINGLE_PAYMENT_REQUEST = "SINGLE_PAYMENT_REQUEST"
    INVOICE = "INVOICE"
    PURCHASEORDER = "PURCHASEORDER"
    PAYMENT = "PAYMENT"


class MimeType(str, Enum):
    PDF = "application/pdf"
    TXT = "text/plain"
    MSWORD = "application/msword"
    EXCEL = "application/vnd.ms-excel"
    PPT = "application/vnd.ms-powerpoint"
    MARKDOWN = "text/markdown"


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
    source_document_key: SourceDocumentKey

    model_config = ConfigDict(
        frozen=True,
        str_min_length=1,
        extra="forbid",
    )


if __name__ == "__main__":
    data = Document(
        document_group_id=uuid4(),
        document_id=uuid4(),
        document_name="",
        source_system="SAP",
        business_process="SUPPLIER",
        uploaded_by="__main__",
        department="VMF",
        source_uri="/home/san/Documents/Amutha/10305.jpg",
        file_hash="a" * 64,
        file_size_bytes=23,
        document_version=2,
    )

    print(data)
    print(data.model_dump())
    print(data.model_dump_json(indent=2))
