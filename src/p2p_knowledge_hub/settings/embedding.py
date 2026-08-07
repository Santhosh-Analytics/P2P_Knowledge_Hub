from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class EmbeddingSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="P2P_")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", min_length=2
    )
    model_provider: str = Field(default="sentence_transformers", min_length=2)
