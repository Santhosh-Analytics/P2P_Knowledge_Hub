from collections.abc import Iterator

from docx.document import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

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
        pdf_docuemnt = pymupdf.open(document.source_uri)
        pdf_pages: list[DocumentPage] = []
        _log.info(f"Extracting pages from {document.source_uri}")
        for page in pdf_docuemnt:
            doc_page = DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                text=page.get_text("text"),
                page_no=page.number + 1,
            )
            pdf_pages.append(doc_page)
        return pdf_pages


class DOCXLoader(BaseLoader):
    def load(self, document: Document) -> list[DocumentPage]:
        docx_document = docx.Document(document.source_uri)
        docx_pages: list[DocumentPage] = []
        current_section: str | None = None
        current_content: list[str] = []

        _log.info(f"Extracting pages from {document.source_uri}")
        for block in self._iter_blocks(docx_document):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if not text:
                    continue
                style_name = block.style.name.strip().lower()

                if style_name == "title":
                    continue

                if style_name == "heading 1":
                    self._flush_section(
                        document=document,
                        docx_pages=docx_pages,
                        section=current_section,
                        content=current_content,
                    )

                    current_section = text
                    current_content = []
                    continue

                # Heading 2 and all other non-empty paragraph styles
                # remain inside the current Heading 1 section.
                current_content.append(text)
            elif isinstance(block, Table):
                table_text = self._extract_table(block)

                if table_text:
                    current_content.append(table_text)

        # Save the final section because no next Heading 1 exists
        # to trigger the normal flush.
        self._flush_section(
            document=document,
            docx_pages=docx_pages,
            section=current_section,
            content=current_content,
        )
        _log.info(
            "DOCX extraction completed: document_id=%s units=%s",
            document.document_id,
            len(docx_pages),
        )

        return docx_pages

    def _flush_section(
        self,
        document: Document,
        docx_pages: list[DocumentPage],
        section: str | None,
        content: list[str],
    ) -> None:
        if not content:
            return
        docx_pages.append(
            DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                text="\n\n".join(content),
                page_no=None,
                section=section,
            )
        )

    def _extract_table(self, table: Table) -> str:
        rows: list[str] = []

        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]

            if any(cells):
                rows.append(" | ".join(cells))

        return "\n".join(rows)

    def _iter_blocks(self, document: DocxDocument) -> Iterator[Paragraph | Table]:
        for child in document.element.body.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, document)
            elif isinstance(child, CT_Tbl):
                yield Table(child, document)


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
