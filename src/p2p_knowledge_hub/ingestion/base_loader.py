from abc import abstractmethod, ABC
from p2p_knowledge_hub.models.document_page_chunk import DocumentPage
from p2p_knowledge_hub.models.document import Document


class BaseLoader(ABC):
    @abstractmethod
    def load(self, document: Document) -> list[DocumentPage]:
        raise NotImplementedError
