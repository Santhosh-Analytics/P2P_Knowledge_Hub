from abc import ABC, abstractmethod
from p2p_knowledge_hub.models import RetrievedChunk


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError
