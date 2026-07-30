from p2p_knowledge_hub.exceptions import sqlalchemy_error
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.models import document
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.models.document_page_chunk import DocumentPage, DocumentChunk
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader
from pathlib import Path
from p2p_knowledge_hub.models.document import (
    Department,
    Document,
    DocumentStatus,
    MimeType,
    SourceDocumentKey,
)

import pymupdf
import docx

settings = get_settings()

_log = AppLogger(settings.logs).get_logger(__name__)


class PDFLoader(BaseLoader):
    def load(self, document: Document) -> list[DocumentPage]:
        doc = pymupdf.open(document.source_uri)
        doc_pages = []
        for page in doc:
            doc_page = DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                text=page.get_text("text"),
                page_no=page.number + 1,
            )
            doc_pages.append(doc_page)
        return doc_pages


class DOCXLoader(BaseLoader):
    def load(self, document: Document) -> list[DocumentPage]:
        doc = docx.Document(document.source_uri)
        doc_pages = []
        for para in doc.paragraphs:
            doc_page = DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                text=para.text
                if (para.text.strip() and "Title" not in para.style.name)
                else None,
                page_no=None,
                section=None,
                title=para.style.name,
            )
            doc_pages.append(doc_page)
        return doc_pages


def valid_document_data():
    return {
        "document_group_id": uuid4(),
        "document_id": uuid4(),
        "document_name": "supplier_policy.pdf",
        "source_system": SourceSystem.TALLY,
        "business_process": BusinessProcess.INVOICE,
        "uploaded_by": "san",
        "uploaded_at": datetime.now(),
        "department": Department.FINANCE,
        # "source_uri": "/home/san/Projects/EnterpriseKnowledgeAssistant_bak/data/raw/Vendor onboarding Policy/SOP Accounts - Payable.pdf",
        "source_uri": "./Training proposal.docx",
        "file_size_bytes": 23,
        "document_version": 1,
        "document_status": DocumentStatus.INDEXED,
        "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
        "mime_type": MimeType.PDF,
        "source_document_key": SourceDocumentKey.CONTRACTING_POLICY,
    }


if __name__ == "__main__":
    from uuid import uuid4
    from p2p_knowledge_hub.models.document import (
        SourceSystem,
        BusinessProcess,
        Department,
        DocumentStatus,
        MimeType,
    )
    from p2p_knowledge_hub.ingestion.hashing import compute_sha256
    from datetime import datetime

    document = Document(**valid_document_data())
    # loader = PDFLoader().load(document)
    loader = DOCXLoader().load(document)

    print(loader)
