from sqlalchemy import create_engine
from p2p_knowledge_hub.settings.main import Settings, get_settings
from sqlalchemy.orm import Session, sessionmaker
from collections.abc import Generator


class SessionManager:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.engine = create_engine(
            self.settings.db.database_url,
            echo=self.settings.db.echo,
            pool_size=self.settings.db.pool_size,
            max_overflow=self.settings.db.max_overflow,
            pool_timeout=self.settings.db.pool_timeout,
            pool_recycle=self.settings.db.pool_recycle,
            pool_pre_ping=self.settings.db.pool_pre_ping,
        )

        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=True, expire_on_commit=False
        )


# manager = SessionManager()
# print(type(manager.session_factory()))

# engine = create_engine(
#     settings.db.database_url,
#     echo=settings.db.echo,
#     pool_size=settings.db.pool_size,
#     max_overflow=settings.db.max_overflow,
#     pool_timeout=settings.db.pool_timeout,
#     pool_recycle=settings.db.pool_recycle,
#     pool_pre_ping=settings.db.pool_pre_ping,
# )
#
#
# SessionFactory = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)
#

# def get_session() -> Generator[Session, None, None]:
#     session = SessionFactory()
#     try:
#         yield session
#         session.commit()
#     finally:
#         session.close()
