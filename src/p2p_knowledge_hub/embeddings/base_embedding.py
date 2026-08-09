from abc import ABC, abstractmethod

from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding


class BaseEmbeddingService(ABC):
    @abstractmethod
    def embed(self, chunks: list[DocumentChunk]) -> list[DocumentEmbedding]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        raise NotImplementedError
