from abc import ABC, abstractmethod
from rank_bm25 import BM25Okapi

from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk


class BaseLexicalIndex(ABC):
    @abstractmethod
    def build(self, chunks: list[DocumentChunk]) -> None:
        raise NotImplementedError

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        raise NotImplementedError
