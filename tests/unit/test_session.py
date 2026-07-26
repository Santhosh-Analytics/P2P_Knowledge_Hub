from p2p_knowledge_hub.models.db.sessions import SessionManager
from sqlalchemy.orm import Session
from sqlalchemy import text


def test_session_manager_creates_engine_and_factory():
    manager = SessionManager()

    assert manager.engine is not None
    assert manager.session_factory is not None


def test_session_factory_creates_orm_session():
    manager = SessionManager()
    session = manager.session_factory()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_session_configuration():
    manager = SessionManager()

    session = manager.session_factory()

    try:
        assert session.autoflush is True
        assert session.expire_on_commit is False
        assert session.bind is manager.engine
    finally:
        session.close()


def test_session_connection_with_database():
    session = SessionManager().session_factory()

    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
    finally:
        session.close()
