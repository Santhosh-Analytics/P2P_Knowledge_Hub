from sqlalchemy import create_engine
from p2p_knowledge_hub.settings.main import get_settings
from sqlalchemy.orm import Session, sessionmaker
from p2p_knowledge_hub.exceptions.base import DBSessionError
from collections.abc import Generator

settings = get_settings()

engine = create_engine(
    settings.db.database_url,
    echo=settings.db.echo,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
    pool_timeout=settings.db.pool_timeout,
    pool_recycle=settings.db.pool_recycle,
    pool_pre_ping=settings.db.pool_pre_ping,
)


SessionFactory = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionFactory()
    try:
        yield session
        session.commit()
    finally:
        session.close()
