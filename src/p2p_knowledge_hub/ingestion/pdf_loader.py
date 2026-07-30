from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.models.document_page_chunk import DocumentPage
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader
from p2p_knowledge_hub.models.document import Document

import pymupdf

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
