from abc import abstractmethod, ABC

from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk, DocumentPage


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, pages: list[DocumentPage]) -> list[DocumentChunk]:
        raise NotImplementedError
