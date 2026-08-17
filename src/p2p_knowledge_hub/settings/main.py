from functools import lru_cache
from p2p_knowledge_hub.settings.exceptions import ExceptionSettings
from p2p_knowledge_hub.settings.logging_config import LogSettings
from p2p_knowledge_hub.settings.chunking import ChunkSettings
from p2p_knowledge_hub.settings.run_time_config import RunTimeDir
from p2p_knowledge_hub.settings.reranker import RerankerSettings
from p2p_knowledge_hub.settings.embedding import EmbeddingSettings
from p2p_knowledge_hub.settings.db import DBConfig
from p2p_knowledge_hub.settings.generation import GenerationSettings
from pathlib import Path
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

_base_dir = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    hf_token: str | None = None
    app_name: str = Field(default="P2P Knowledge Hub", min_length=4)
    runtime_dir: RunTimeDir = Field(default_factory=RunTimeDir)
    logs: LogSettings = Field(default_factory=LogSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    chunks: ChunkSettings = Field(default_factory=ChunkSettings)
    exceptions: ExceptionSettings = Field(default_factory=ExceptionSettings)
    db: DBConfig = Field(default_factory=DBConfig)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    # chunks
    model_config = SettingsConfigDict(
        toml_file=_base_dir / "config.toml",
        env_prefix="p2p_",
        env_nested_delimiter="__",
        env_file=_base_dir / ".env",
        env_ignore_empty=False,
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
            init_settings,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    return s


if __name__ == "__main__":
    s = get_settings()
    print(s.model_dump())
    print(s.model_dump_json())
    print(_base_dir)
