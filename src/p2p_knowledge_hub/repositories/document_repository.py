from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from p2p_knowledge_hub.models.document import (
    Department,
    Document,
    SourceDocumentKey,
    SourceSystem,
    BusinessProcess,
)
from p2p_knowledge_hub.repositories.base_repository import AbstractDocumentRepository
from p2p_knowledge_hub.models.db.document import DocumentRecord
from p2p_knowledge_hub.exceptions.base import DocumentNotFoundException


class SQLAlchemyDocumentRepository(AbstractDocumentRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, document: Document) -> None:
        self.session.add(DocumentRecord(**document.model_dump()))

    def get(self, document_id: UUID) -> Document:
        doc = self._get(document_id)

        return self._to_domain(doc)

    def _get(self, document_id: UUID) -> DocumentRecord:
        doc = self.session.get(DocumentRecord, document_id)

        if doc is None:
            raise DocumentNotFoundException(f"No Document found with id:{document_id}")
        else:
            return doc

    def delete(self, document_id: UUID) -> None:
        self.session.delete(self._get(document_id))

    def find_exact_duplicate(
        self,
        source_system: SourceSystem,
        business_process: BusinessProcess,
        department: Department,
        file_hash: str,
        source_document_key: SourceDocumentKey,
    ) -> Document | None:
        stmt = select(DocumentRecord).where(
            DocumentRecord.business_process == business_process,
            DocumentRecord.source_system == source_system,
            DocumentRecord.department == department,
            DocumentRecord.file_hash == file_hash,
            DocumentRecord.source_document_key == source_document_key,
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        if result is not None:
            return self._to_domain(result)

    def find_latest_version(
        self,
        source_system: SourceSystem,
        business_process: BusinessProcess,
        department: Department,
        source_document_key: SourceDocumentKey,
    ) -> Document | None:
        stmt = (
            select(DocumentRecord)
            .where(
                DocumentRecord.business_process == business_process,
                DocumentRecord.source_system == source_system,
                DocumentRecord.department == department,
                DocumentRecord.source_document_key == source_document_key,
            )
            .order_by(desc(DocumentRecord.document_version))
        ).limit(1)
        result = self.session.execute(stmt).scalar_one_or_none()

        if result is not None:
            return self._to_domain(result)

    def _to_domain(self, record: DocumentRecord) -> Document:
        document = Document(
            document_id=record.document_id,
            document_group_id=record.document_group_id,
            document_name=record.document_name,
            document_status=record.document_status,
            document_version=record.document_version,
            source_system=record.source_system,
            business_process=record.business_process,
            uploaded_at=record.uploaded_at,
            uploaded_by=record.uploaded_by,
            department=record.department,
            source_uri=record.source_uri,
            file_hash=record.file_hash,
            file_size_bytes=record.file_size_bytes,
            mime_type=record.mime_type,
            source_document_key=record.source_document_key,
        )
        return document
