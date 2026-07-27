from datetime import datetime
from pathlib import Path
import pytest
from p2p_knowledge_hub.exceptions.base import DocumentNotFoundException
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from p2p_knowledge_hub.models.db.sessions import SessionManager
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    Department,
    Document,
    MimeType,
    SourceSystem,
    DocumentStatus,
)
from p2p_knowledge_hub.models.db.document import DocumentRecord
from p2p_knowledge_hub.repositories.document_repository import (
    SQLAlchemyDocumentRepository,
)
from uuid import uuid4
from p2p_knowledge_hub.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork


@pytest.fixture
def valid_document_data():
    return {
        "document_group_id": uuid4(),
        "document_id": uuid4(),
        "document_name": "supplier_policy.pdf",
        "source_system": SourceSystem.TALLY,
        "business_process": BusinessProcess.INVOICE,
        "uploaded_by": "san",
        "uploaded_at": datetime.now(),
        "department": Department.PAYMENT,
        "source_uri": "/tmp/supplier_policy.pdf",
        "file_size_bytes": 23,
        "document_version": 1,
        "document_status": DocumentStatus.INDEXED,
        "file_hash": compute_sha256(Path("/home/san/config.txt")),
        "mime_type": MimeType.PDF,
        "source_document_key": "SUPPLIER_POLICY_001",
    }


def test_unit_of_work_add_commit_get_commit_delete_commit(valid_document_data):
    doc_schema = Document(**valid_document_data)
    with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
        doc_record = DocumentRecord(**doc_schema.model_dump())
        uow.document.add(doc_record)
        uow.commit()

    with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
        fetched = uow.document.get(doc_record.document_id)

        assert fetched is not None
        assert fetched.document_id == doc_record.document_id
        assert fetched.document_id == doc_record.document_id

    with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
        uow.document.delete(doc_record.document_id)
        uow.session.flush()
        uow.commit()
        with pytest.raises(DocumentNotFoundException):
            uow.document.get(doc_record.document_id)


def test_unit_of_work_rollback(valid_document_data):
    doc_schema = Document(**valid_document_data)
    with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
        doc_record = DocumentRecord(**doc_schema.model_dump())
        uow.document.add(doc_record)

    with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
        with pytest.raises(DocumentNotFoundException):
            uow.document.get(doc_record.document_id)
