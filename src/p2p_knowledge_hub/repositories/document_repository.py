from uuid import UUID

from sqlalchemy.orm import Session

from p2p_knowledge_hub.repositories.base_repository import AbstractDocumentRepository
from p2p_knowledge_hub.models.db.document import DocumentRecord
from p2p_knowledge_hub.exceptions.base import DocumentNotFoundException


class SQLAlchemyDocumentRepository(AbstractDocumentRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, document: DocumentRecord) -> None:
        self.session.add(document)

    def get(self, document_id: UUID) -> DocumentRecord | None:
        doc = self.session.get(DocumentRecord, document_id)

        if doc is None:
            raise DocumentNotFoundException(f"No Document found with id:{document_id}")
        else:
            return doc

    def delete(self, document_id: UUID) -> None:
        self.session.delete(self.get(document_id))
