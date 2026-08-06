from abc import ABC, abstractmethod
from rank_bm25 import BM25Okapi
from p2p_knowledge_hub.models import DocumentChunk, RetrievedChunk


class BaseLexicalIndex(ABC):
    @abstractmethod
    def build(self, chunks: list[DocumentChunk]) -> None:
        raise NotImplementedError

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        raise NotImplementedError
