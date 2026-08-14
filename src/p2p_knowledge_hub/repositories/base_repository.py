from abc import ABC, abstractmethod
from uuid import UUID
from p2p_knowledge_hub.models.db.document import DocumentRecord
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    SourceSystem,
    Department,
    SourceDocumentKey,
)


class AbstractDocumentRepository(ABC):
    @abstractmethod
    def add(self, document: Document) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, document_id: UUID) -> Document:
        raise NotImplementedError

    @abstractmethod
    def delete(self, document_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_exact_duplicate(
        self,
        source_system: SourceSystem,
        business_process: BusinessProcess,
        department: Department,
        file_hash: str,
        source_document_key: SourceDocumentKey,
    ) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_ids(self, ids: set[UUID]) -> dict[UUID, Document]:
        raise NotImplementedError

    @abstractmethod
    def find_latest_version(
        self,
        source_system: SourceSystem,
        business_process: BusinessProcess,
        department: Department,
        source_document_key: SourceDocumentKey,
    ) -> Document | None:
        raise NotImplementedError
