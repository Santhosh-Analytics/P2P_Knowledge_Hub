from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from p2p_knowledge_hub.repositories.document_repository import (
    SQLAlchemyDocumentRepository,
)
from p2p_knowledge_hub.unit_of_work.base import AbstractUnitOfWork
from p2p_knowledge_hub.exceptions.sqlalchemy_error import (
    DBConnectionError,
    DBConstraintError,
    DBNotnullError,
    DBSyntexError,
    DBUnknownError,
)


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory
        self.session: Session
        self.document: SQLAlchemyDocumentRepository

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
        try:
            self.session.commit()
        except IntegrityError as e:
            error_message = str(e.__dict__.get("orig", e))
            if "duplicate key value violates unique constraint" in error_message:
                raise DBConstraintError(f"{error_message}")
            elif str(23502) in error_message:
                raise DBNotnullError(f"{error_message}")
            else:
                raise DBUnknownError(f"{error_message}")
        except ProgrammingError as e:
            error_message = str(e.__dict__.get("orig", e))
            raise DBSyntexError(f"{error_message}")
        except OperationalError as e:
            error_message = str(e.__dict__.get("orig", e))
            if "connection failed: connection to server" in error_message:
                raise DBConnectionError(f"{error_message}")

    def rollback(self) -> None:
        self.session.rollback()
