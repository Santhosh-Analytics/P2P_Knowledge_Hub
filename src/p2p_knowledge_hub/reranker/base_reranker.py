from abc import ABC, abstractmethod

from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk


class BaseReranker(ABC):
    @abstractmethod
    def rerank(
        self, query: str, retrieved: list[RetrievedChunk], top_k: int
    ) -> list[RetrievedChunk]:
        raise NotImplementedError
