from pydoc import text

from p2p_knowledge_hub.chunking.base_chunker import BaseChunker
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    Department,
    DocumentStatus,
    MimeType,
    SourceSystem,
    tz_aware_time,
)
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk, DocumentPage
from p2p_knowledge_hub.settings.main import get_settings

# from p2p_knowledge_hub.exceptions import chunking_exception
from p2p_knowledge_hub.core.logger import AppLogger


settings = get_settings()
_log = AppLogger(settings.logs).get_logger()


class FixedChunker(BaseChunker):
    def chunk(self, pages: list[DcumentPage]) -> list[DocumentChunk]:
        document_chunks: list[DocumentChunk] = []
        for page in pages:
            chunks = self._chunker(page, 10, 3)
            document_chunks.append(
                DocumentChunk(
                    chunk_id=uuid4(),
                    chunk_index=page.document_group_id,
                    chunking_version=1,
                    document_id=page.uuid,
                    document_group_id=page.document_group_id,
                    is_active=True,
                    created_at=tz_aware_time(),
                    text=chunks,
                )
            )
        return document_chunks

    def _chunker(page: DocumentPage, chunk_size: int, chunk_overlap: int) -> list[str]:
        chunks: list[str] = []
        for i in range(0, len(page.text.split(), chunk_size - chunk_overlap)):
            chunk = " ".join(page.text.split()[i : i + cs])
            chunks.append(chunk)
        return chunks


if __name__ == "__main__":
    from p2p_knowledge_hub.ingestion.markdown_loader import MarkDownLoader
    from p2p_knowledge_hub.ingestion.hashing import compute_sha256
    from uuid import uuid4
    from p2p_knowledge_hub.models.document import (
        Document,
        SourceDocumentKey,
        SourceSystem,
        BusinessProcess,
        Department,
        DocumentStatus,
        MimeType,
    )
    from datetime import datetime
    from pathlib import Path

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
            "source_uri": "/home/san/Obsidian/Data Science/Machine Learning/1. Linear Regression/0. Conclusion.md",
            "file_size_bytes": 23,
            "document_version": 1,
            "document_status": DocumentStatus.INDEXED,
            "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
            "mime_type": MimeType.PDF,
            "source_document_key": SourceDocumentKey.CONTRACTING_POLICY,
        }

    document = Document(**valid_document_data())
    loader = MarkDownLoader().load(document)

    fixed_chunker = FixedChunker()
    ssw = fixed_chunker.chunk(loader)
    print(ssw)
