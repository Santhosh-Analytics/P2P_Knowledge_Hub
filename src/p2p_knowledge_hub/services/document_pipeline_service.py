from uuid import uuid4
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
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
)
from p2p_knowledge_hub.services.ingestion_service import IngestionService
from p2p_knowledge_hub.ingestion.loader_factory import DocumentLoaderFactory
from p2p_knowledge_hub.services.indexing_services import IndexingService
from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore

settings = get_settings()


class DocumentPipelineService:
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
    ):

        stored_path = LocalFileStorage().store(file_bytes, file_name)
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
            mime_type=content_type,
            file_size_bytes=file_size,
            source_uri=str(stored_path),
        )

        IngestionService().ingestion_service(document)
        loader = DocumentLoaderFactory().get_loader(Path(document.source_uri))
        pages = loader.load(document)

        chunks = RecursiveChunker().chunk(pages)
        embedding_service = SentenceTransformerEmbedding(
            model_name=settings.embeddings.embedding_model
        )

        chroma_client = chromadb.PersistentClient(
            path=Path(settings.runtime_dir.base_dir / "chroma"),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        vector_store = ChromaVectorStore(client=chroma_client)
        index_service = IndexingService(embedding_service, vector_store)
        index_service.index(chunks)
