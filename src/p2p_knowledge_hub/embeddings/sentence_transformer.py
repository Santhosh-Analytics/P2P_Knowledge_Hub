from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.exceptions.chunking_exceptions import P2PHubException
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
from p2p_knowledge_hub.models.document import tz_aware_time

from sentence_transformers import SentenceTransformer

settings = get_settings()
_log = AppLogger(settings.logs).get_logger(__name__)


class SentenceTransformerEmbedding(BaseEmbeddingService):
    def __init__(self, model_name: str, provider: str = "SentenceTransformer") -> None:
        self.model_name = model_name
        self.provider = provider
        self.model = SentenceTransformer(model_name)

    def embed(self, chunks: list[DocumentChunk]) -> list[DocumentEmbedding]:
        for chunk in chunks:
            if not chunk.text.strip():
                raise ValueError(f"Chunk {chunk.chunk_id} contains empty text")

        document_embedding: list[DocumentEmbedding] = []
        embed_text = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(embed_text, normalize_embeddings=True)

        for embed_chunk, chunk in zip(embeddings, chunks):
            document_embedding.append(
                DocumentEmbedding(
                    chunk_id=chunk.chunk_id,
                    embeddings=embed_chunk.tolist(),
                    embedding_provider=self.provider,
                    embedding_model=self.model_name,
                    created_at=tz_aware_time(),
                    embedding_dimension=len(embed_chunk),
                )
            )
        return document_embedding

    def embed_query(self, query: str) -> list[float]:
        query_embeddings: list[float] = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return query_embeddings.tolist()
