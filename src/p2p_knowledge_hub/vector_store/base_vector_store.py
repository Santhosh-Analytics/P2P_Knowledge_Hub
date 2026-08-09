from abc import ABC, abstractmethod

from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk


class BaseVectorStore(ABC):
    @abstractmethod
    def upsert(
        self, chunks: list[DocumentChunk], embeddings: list[DocumentEmbedding]
    ) -> None:
        raise NotImplementedError

    def search(self, query_embeddings: list[float], top_k: int) -> list[RetrievedChunk]:
        raise NotImplementedError
