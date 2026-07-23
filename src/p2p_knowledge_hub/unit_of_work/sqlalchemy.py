from sqlalchemy.orm import Session

from p2p_knowledge_hub.unit_of_work.base import AbstractUnitOfWork
from p2p_knowledge_hub.models.db.sessions import SessionFactory


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: Session) -> None:
        self.session = SessionFactory()

    def __enter__(self) -> "AbstractUnitOfWork":
        self.session = SessionFactory()
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
