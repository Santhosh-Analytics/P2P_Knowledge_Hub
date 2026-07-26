# from sqlalchemy import text
# from p2p_knowledge_hub.models.db.document import DocumentRecord
# from p2p_knowledge_hub.models.db.base import Base
#
#
# from p2p_knowledge_hub.models.db.sessions import engine
#
#
# def check_database_connection() -> None:
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT 1"))
#         value = result.scalar_one()
#
#         if value != 1:
#             raise RuntimeError("Unexpected database response")
#
#         print("PostgreSQL connection successful")
#
#
# if __name__ == "__main__":
#     check_database_connection()
#     print(Base.metadata.tables)
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError
import pytest
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from p2p_knowledge_hub.models.db.document import DocumentRecord
from p2p_knowledge_hub.models.db.sessions import SessionManager
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    Department,
    Document,
    MimeType,
    SourceSystem,
    DocumentStatus,
)
from uuid import uuid4

from p2p_knowledge_hub.repositories.document_repository import (
    SQLAlchemyDocumentRepository,
)


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
    }


repo = SQLAlchemyDocumentRepository(session=SessionManager().session_factory())
document_schema = Document(**valid_document_data())
doc_record = DocumentRecord(**document_schema.model_dump())
repo.add(document=doc_record)
