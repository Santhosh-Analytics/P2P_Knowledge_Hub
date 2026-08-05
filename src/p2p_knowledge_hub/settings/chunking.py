from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict, BaseSettings
from enum import StrEnum


class ChunkStrategy(StrEnum):
    sliding_window = "sliding_window"
    recursive = "recursive"
    semantic = "semantic"


class ChunkSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="P2P_")

    chunk_strategy: ChunkStrategy = Field(default=ChunkStrategy.recursive)
    max_chunk_size: int = Field(default=70, ge=0)
    chunk_overlap: int | None = Field(default=None, ge=40)
    semantic_similarity_threshold: float = Field(default=0.85, gt=0, le=1)

    @model_validator(mode="after")
    def validate_chunk_settings(self) -> "ChunkSettings":
        if self.chunk_overlap is None:
            self.chunk_overlap = int(self.max_chunk_size * 0.1)
        if self.chunk_overlap >= self.max_chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.max_chunk_size})"
            )
        return self
