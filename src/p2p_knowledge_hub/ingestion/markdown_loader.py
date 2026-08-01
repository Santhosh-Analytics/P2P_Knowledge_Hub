from turtle import title

from rich import print
from uuid import uuid4
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader
from p2p_knowledge_hub.models.document import (
    SourceSystem,
    BusinessProcess,
    Department,
    DocumentStatus,
    SourceDocumentKey,
    MimeType,
)
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from datetime import datetime
from pathlib import Path

from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.exceptions.base import (
    DocumentLoadError,
    FileMissingError,
    FilePermissionError,
    FileReadError,
)
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.models.document_page_chunk import DocumentPage
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader
from p2p_knowledge_hub.models.document import Document

settings = get_settings()

_log = AppLogger(settings.logs).get_logger(__name__)


class MarkDownLoader(BaseLoader):
    def load(self, document: Document) -> list[DocumentPage]:
        md_pages: list[DocumentPage] = []
        current_section: str | None = None
        current_content: list[str] = []
        current_title: str | None = None

        try:
            with open(document.source_uri, "r", encoding="utf-8") as f:
                md_doc = f.read()
        except PermissionError as exc:
            raise FilePermissionError(
                message=f"Permission denied while reading {document.source_uri}"
            ) from exc

        except FileNotFoundError as exc:
            raise FileMissingError(
                f"File was not found: {document.source_uri}"
            ) from exc

        except OSError as exc:
            _log.error(
                f"Expected a file path, but got a directory:{document.source_uri}"
            )
            raise FileReadError(
                f"Unable to read markdown file: {document.source_uri}"
            ) from exc
        except UnicodeDecodeError as exc:
            raise DocumentLoadError(
                f"Unable to read markdown file, Invalid unicode: {document.source_uri}"
            ) from exc

        for line in md_doc.splitlines(keepends=True):
            if line.startswith("# "):
                self._flush_section(
                    document=document,
                    md_pages=md_pages,
                    section=current_section,
                    content=current_content,
                    title=current_title,
                )
                current_title = line.removeprefix("#").strip()
                current_section = None

                current_content = []

                continue
            elif line.startswith("## "):
                self._flush_section(
                    document=document,
                    md_pages=md_pages,
                    section=current_section,
                    content=current_content,
                    title=current_title,
                )
                current_section = line.removeprefix("## ").strip()
                current_content = []
                continue

            current_content.append(line)

        self._flush_section(
            document=document,
            md_pages=md_pages,
            section=current_section,
            content=current_content,
            title=current_title,
        )
        _log.info(
            "Markdown extraction completed: document_id=%s units=%s",
            document.document_id,
            len(md_pages),
        )

        return md_pages

    def _flush_section(
        self,
        document: Document,
        md_pages: list[DocumentPage],
        section: str | None,
        content: list[str],
        title: str | None,
    ) -> None:
        if not content:
            return

        md_pages.append(
            DocumentPage(
                document_id=document.document_id,
                document_group_id=document.document_group_id,
                section=section,
                text="".join(content),
                title=title,
            )
        )


if __name__ == "__main__":

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
    try:
        loader = MarkDownLoader().load(document)
    except FileMissingError as exc:
        print(f"[bold red blink]File not found: {exc}")
    except FilePermissionError as exc:
        print(f"[bold red blink]Permission denied: {exc}")
    except DocumentLoadError as exc:
        print(f"[bold red blink]DOCX loading failed: {exc}")
    except FileReadError as exc:
        print(f"[bold red blink]Unable to read DOCX file: {exc}")
    except IsADirectoryError as exc:
        print(f"[bold red blink]Expected a file path, but got a directory: {exc}")
    else:
        print(loader)
