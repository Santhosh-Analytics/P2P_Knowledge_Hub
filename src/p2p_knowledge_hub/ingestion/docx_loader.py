from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.models.document_page_chunk import DocumentPage
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader
from p2p_knowledge_hub.models.document import Document

import docx
from docx.shared import Inches

settings = get_settings()

_log = AppLogger(settings.logs).get_logger(__name__)


class DOCXLoader(BaseLoader):
    def load(self, document: Document) -> list[DocumentPage]:
        doc = docx.Document(document.source_uri)
        doc_pages = []
        for para, table in zip(doc.paragraphs, doc.tables):
            cell_text = [cell.text for row in table.rows for cell in row.cells]
            doc_page = DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                text=para.text if para else cell_text,
                page_no=None,
                section=None,
            )
            doc_pages.append(doc_page)
        return doc_pages
