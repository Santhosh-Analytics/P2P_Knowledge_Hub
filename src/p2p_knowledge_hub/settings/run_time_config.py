from pydantic import model_validator, Field
from pathlib import Path
from typing import Any
from pydantic_settings import SettingsConfigDict, BaseSettings


class RunTimeDir(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="p2p_", env_file=".env", extra="ignore"
    )
    base_dir: Path = Field(default_factory=lambda: Path(__file__).absolute().parents[3])

    logs_dir: Path
    artifacts_dir: Path
    tests_dir: Path
    data_dir: Path
    docs_dir: Path

    raw_data_dir: Path
    processed_data_dir: Path
    test_data_dir: Path

    @model_validator(mode="before")
    @classmethod
    def resolve_paths(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        base_dir = Path(
            data.get(
                "base_dir",
                Path(__file__).absolute().parents[3],
            )
        )

        data.setdefault("logs_dir", base_dir / "logs")
        data.setdefault("data_dir", base_dir / "data")
        data.setdefault("tests_dir", base_dir / "test")
        data.setdefault("artifacts_dir", base_dir / "artifacts")
        data.setdefault("docs_dir", base_dir / "docs")

        data_dir = Path(data["data_dir"])

        data.setdefault("raw_data_dir", data_dir / "raw")
        data.setdefault("processed_data_dir", data_dir / "processed")
        data.setdefault("test_data_dir", data_dir / "test_data")

        return data

    @model_validator(mode="after")
    def create_runtime_dir(self) -> "RunTimeDir":
        directories = (
            self.logs_dir,
            self.artifacts_dir,
            self.tests_dir,
            self.data_dir,
            self.docs_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.test_data_dir,
        )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return self
