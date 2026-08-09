from pathlib import Path
from p2p_knowledge_hub.ingestion.markdown_loader import MarkDownLoader
from p2p_knowledge_hub.ingestion.pdf_loader import PDFLoader
from p2p_knowledge_hub.ingestion.docx_loader import DOCXLoader
from p2p_knowledge_hub.ingestion.base_loader import BaseLoader


class DocumentLoaderFactory:
    def get_loader(self, source_uri: Path) -> BaseLoader:
        loaders = {".pdf": PDFLoader, ".md": MarkDownLoader, ".docx": DOCXLoader}
        identifier = Path(source_uri).suffix.lower()
        loader_class = loaders[identifier]

        return loader_class()
