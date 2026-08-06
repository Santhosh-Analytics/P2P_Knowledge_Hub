from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from p2p_knowledge_hub.exceptions.chunking_exceptions import P2PHubException
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
from p2p_knowledge_hub.models.document import tz_aware_time
from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore


settings = get_settings()
_log = AppLogger(settings.logs).get_logger(__name__)


class IndexingService:
    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vec_store: BaseVectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vec_store = vec_store

    def index(self, chunks: list[DocumentChunk]) -> None:
        embeddings = self.embedding_service.embed(chunks)
        self.vec_store.upsert(chunks, embeddings)
