from sqlalchemy.orm import sessionmaker

from p2p_knowledge_hub.repositories.document_repository import (
    SQLAlchemyDocumentRepository,
)
from p2p_knowledge_hub.unit_of_work.base import AbstractUnitOfWork


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.document = SQLAlchemyDocumentRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
