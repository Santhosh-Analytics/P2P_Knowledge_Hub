from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    Uuid,
    Enum,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from p2p_knowledge_hub.models.db.base import Base
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    DocumentStatus,
    MimeType,
    SourceSystem,
)


class DocumentRecord(Base):
    __tablename__ = "documents"
    document_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[SourceSystem] = mapped_column(
        Enum(SourceSystem, name="source_system_enum"), nullable=False
    )
    business_process: Mapped[BusinessProcess] = mapped_column(
        Enum(BusinessProcess, name="business_process_enum"), nullable=False
    )
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    document_status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status_enum"), nullable=False
    )
    document_version: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[MimeType] = mapped_column(
        Enum(MimeType, name="mime_type_enum"), nullable=False
    )
    source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    __table_args__ = (
        CheckConstraint(
            "document_version >= 1",
            name="ck_documents_version_positive",
        ),
        CheckConstraint("char_length(file_hash) = 64", name="ck_documents_hash_length"),
        UniqueConstraint(
            "source_system",
            "business_process",
            "file_hash",
            name="uq_documents_source_process_hash",
        ),
    )
