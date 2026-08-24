from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.exceptions.chunking_exceptions import NoChunksProducedError
from uuid import uuid4
from pathlib import Path
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk, DocumentPage
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from p2p_knowledge_hub.storage.local_file_storage import LocalFileStorage
from p2p_knowledge_hub.models.document import (
    Department,
    DocumentStatus,
    SourceDocumentKey,
    Document,
    SourceSystem,
    BusinessProcess,
    MimeType,
)
from p2p_knowledge_hub.models.api.document_upload import DocumentUploadResponse
from p2p_knowledge_hub.services.ingestion_service import IngestionService
from p2p_knowledge_hub.ingestion.loader_factory import DocumentLoaderFactory
from p2p_knowledge_hub.services.ingestion_service import (
    MetadataCollector,
)
from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
from p2p_knowledge_hub.services.indexing_services import IndexingService
from rich import print

settings = get_settings()

_log = AppLogger(settings.logs).get_logger(__name__)


class DocumentPipelineService:
    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
    ) -> None:
        self.metadata_collector = MetadataCollector()
        self.ingestion_service = IngestionService()
        self.loader_factory = DocumentLoaderFactory()
        self.chunker = RecursiveChunker()
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.index_service = IndexingService(self.embedding_service, self.vector_store)
        self.file_storage = LocalFileStorage()

    def metadata_ingestion(self, document: Document) -> None:
        self.ingestion_service.ingestion_service(document)

    def document_pipeline(self, document: Document) -> int:
        pages: list[DocumentPage] = self.loader_factory.get_loader(
            Path(document.source_uri)
        ).load(document)
        chunks: list[DocumentChunk] = self.chunker.chunk(pages)

        self.index_service.index(chunks)

        return len(chunks)

    async def process_upload(
        self,
        file_bytes: bytes,
        file_name: str,
        file_size: int,
        content_type: str | None,
        source_system: SourceSystem,
        business_process: BusinessProcess,
        department: Department,
        source_document_key: SourceDocumentKey,
        uploaded_by: str,
    ) -> DocumentUploadResponse:

        stored_path = self.file_storage.store(file_bytes, file_name)
        if content_type is None:
            raise ValueError("Missing content type")

        mime_type = MimeType(content_type)

        document = Document(
            document_id=uuid4(),
            document_group_id=uuid4(),
            document_name=file_name,
            document_status=DocumentStatus.UPLOADED,
            uploaded_by=uploaded_by,
            file_hash=compute_sha256(stored_path),
            department=department,
            business_process=business_process,
            source_document_key=source_document_key,
            source_system=source_system,
            mime_type=mime_type,
            file_size_bytes=file_size,
            source_uri=str(stored_path),
        )
        self.ingestion_service.ingestion_service(document)
        self.ingestion_service.update_status(
            id=document.document_id, status=DocumentStatus.PROCESSING
        )
        try:
            chunks_len = self.document_pipeline(document)

            self.ingestion_service.update_status(
                id=document.document_id, status=DocumentStatus.INDEXED
            )
            indexed_document = document.model_copy(
                update={"document_status": DocumentStatus.INDEXED}
            )

            document_upload_response = DocumentUploadResponse(
                **indexed_document.model_dump(),
                chunks_length=chunks_len,
            )
            return document_upload_response

        except NoChunksProducedError as exc:
            self.ingestion_service.update_status(
                id=document.document_id, status=DocumentStatus.FAILED
            )
            _log.error(f"[bold red blink] ERROR: Unable produce chunks. {exc}")
            raise

    def cli_metadata_collector(self, file_path: Path) -> int:
        document: Document = self.metadata_collector.collect_document(file_path)
        self.metadata_ingestion(document)
        chunks_length = self.document_pipeline(document)

        return chunks_length
