from sqlalchemy import text

from p2p_knowledge_hub.models.db.sessions import engine


def check_database_connection() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar_one()

        if value != 1:
            raise RuntimeError("Unexpected database response")

        print("PostgreSQL connection successful")


if __name__ == "__main__":
    check_database_connection()
