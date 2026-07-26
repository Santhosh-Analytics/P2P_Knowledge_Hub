from datetime import datetime
from pathlib import Path
import re
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
        "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
        "mime_type": MimeType.PDF,
        "source_document_key": "SUPPLIER_POLICY_001",
    }


def test_repository_add_record(valid_document_data):
    session = SessionManager().session_factory()
    repo = SQLAlchemyDocumentRepository(session)
    try:
        doc_schema = Document(**valid_document_data)
        doc_record = DocumentRecord(**doc_schema.model_dump())
        repo.add(doc_record)
        repo.session.flush()
        fetched = session.get(DocumentRecord, doc_record.document_id)

        assert fetched is not None
        assert fetched.document_id == doc_record.document_id
        assert fetched.business_process == doc_record.business_process
        assert fetched.department == doc_record.department

    finally:
        session.rollback()
        session.close()


def test_repository_get_record(valid_document_data):
    session = SessionManager().session_factory()
    repo = SQLAlchemyDocumentRepository(session)
    try:
        doc_schema = Document(**valid_document_data)
        doc_record = DocumentRecord(**doc_schema.model_dump())
        repo.add(doc_record)
        repo.session.flush()
        fetched = session.get(DocumentRecord, doc_record.document_id)

        get_fetched = repo.get(fetched.document_id)

        assert get_fetched is not None
        assert get_fetched.document_id == doc_record.document_id

    finally:
        session.rollback()
        session.close()


def test_repository_get_record_not_found():
    session = SessionManager().session_factory()
    repo = SQLAlchemyDocumentRepository(session)
    try:
        with pytest.raises(DocumentNotFoundException):
            repo.get(uuid4())
    finally:
        session.rollback()
        session.close()


def test_repository_delete_record(valid_document_data):
    session = SessionManager().session_factory()
    repo = SQLAlchemyDocumentRepository(session)
    try:
        doc_schema = Document(**valid_document_data)
        doc_record = DocumentRecord(**doc_schema.model_dump())
        repo.add(doc_record)
        repo.session.flush()
        repo.delete(doc_record.document_id)
        session.flush()

        with pytest.raises(DocumentNotFoundException):
            repo.get(doc_record.document_id)

    finally:
        session.rollback()
        session.close()
