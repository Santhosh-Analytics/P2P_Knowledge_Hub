from p2p_knowledge_hub.exceptions.chunking_exceptions import P2PHubException
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.chunking.base_chunker import BaseChunker
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk, DocumentPage
from p2p_knowledge_hub.models.document import tz_aware_time
from uuid import uuid4

settings = get_settings()
_log = AppLogger(settings.logs).get_logger(__name__)


class RecursiveChunker(BaseChunker):
    def chunk(self, pages: list[DocumentPage]) -> list[DocumentChunk]:
        document_chunks: list[DocumentChunk] = []
        chunk_idx: int = 1
        for page in pages:
            chunks = self._split_text(
                text=page.text, max_chunk_size=settings.chunks.max_chunk_size
            )
            if not chunks:
                _log.warning(
                    "No chunks produced: document_id=%s section=%s page_no=%s",
                    page.document_id,
                    page.section,
                    page.page_no,
                )
                continue

            for chunk in chunks:
                document_chunks.append(
                    DocumentChunk(
                        chunk_id=uuid4(),
                        chunking_version=1,
                        chunk_index=chunk_idx,
                        document_id=page.document_id,
                        document_group_id=page.document_group_id,
                        is_active=True,
                        created_at=tz_aware_time(),
                        text=chunk,
                        page_no=page.page_no,
                        section=page.section,
                        title=page.title,
                    )
                )
                chunk_idx += 1

        return document_chunks

    def _split_text(
        self,
        text: str,
        max_chunk_size: int,
        separators: tuple[str, ...] = ("\n\n", "\n", ". ", " "),
    ) -> list[str]:

        if not text.strip():
            return []
        if len(text.split()) <= max_chunk_size:
            return [text.strip()]
        if not separators:
            words = text.split()
            return [
                " ".join(words[i : i + max_chunk_size])
                for i in range(0, len(words), max_chunk_size)
            ]

        current_separator = separators[0]
        remaining_separators = separators[1:]
        pieces = text.split(current_separator)
        smaller_pieces: list[str] = []

        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            if len(piece.split()) <= max_chunk_size:
                smaller_pieces.append(piece)
            else:
                smaller_pieces.extend(
                    self._split_text(
                        text=piece,
                        max_chunk_size=max_chunk_size,
                        separators=remaining_separators,
                    ),
                )

        return self._merge_split(
            pieces=smaller_pieces,
            max_chunk_size=max_chunk_size,
            separator=current_separator,
        )

    def _merge_split(
        self, pieces: list[str], max_chunk_size: int, separator: str
    ) -> list[str]:
        chunks: list[str] = []
        current_parts: list[str] = []
        current_word_count = 0

        for piece in pieces:
            piece_word_count = len(piece.split())

            if current_parts and current_word_count + piece_word_count > max_chunk_size:
                chunks.append(separator.join(current_parts).strip())
                current_parts = []
                current_word_count = 0

            current_parts.append(piece)
            current_word_count += piece_word_count

        if current_parts:
            chunks.append(separator.join(current_parts).strip())

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
    chunks = RecursiveChunker().chunk(loader)
    import json

    print(json.dumps([c.model_dump() for c in chunks], indent=2, default=str))
