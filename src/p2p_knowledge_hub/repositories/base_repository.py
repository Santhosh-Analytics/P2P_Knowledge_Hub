from abc import ABC, abstractmethod
from uuid import UUID
from p2p_knowledge_hub.models.db.document import DocumentRecord


class DocumentRepository(ABC):
    @abstractmethod
    def add(self, document: DocumentRecord) -> None:
        pass

    @abstractmethod
    def get(self, document_id: UUID) -> DocumentRecord | None:
        pass

    @abstractmethod
    def delete(self, document_id: UUID) -> None:
        pass
