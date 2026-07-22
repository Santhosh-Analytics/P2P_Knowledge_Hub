from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import URL


class DBConfig(BaseModel):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5432, ge=1, le=65535)
    database: str = Field(default="p2p_knowledge_hub")
    username: str = Field(default="p2p_hub_app")
    password: SecretStr
    driver_name: str = Field(default="postgresql+psycopg")

    echo: bool = Field(default=True)
    pool_size: int = Field(default=5, ge=1, le=20)
    max_overflow: int = Field(default=10, le=50, ge=0)
    pool_timeout: int = Field(default=30, ge=1, le=120)
    pool_recycle: int = Field(default=1800, le=7200, ge=300)
    pool_pre_ping: bool = Field(default=True)

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername=self.driver_name,
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.database,
        )
