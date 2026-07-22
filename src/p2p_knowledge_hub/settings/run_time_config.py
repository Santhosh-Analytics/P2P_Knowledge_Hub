from pydantic import model_validator, Field
from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings


class RunTimeDir(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="p2p_", env_file=".env", extra="ignore"
    )
    base_dir: Path = Field(default_factory=lambda: Path(__file__).absolute().parents[3])

    logs_dir: Path | None = Field(default=None)
    artifacts_dir: Path | None = Field(default=None)
    tests_dir: Path | None = Field(default=None)
    data_dir: Path | None = Field(default=None)

    raw_data_dir: Path | None = Field(default=None)
    processed_data_dir: Path | None = Field(default=None)
    test_data_dir: Path | None = Field(default=None)

    docs_dir: Path | None = Field(default=None)

    @model_validator(mode="after")
    def create_runtime_dir(self) -> "RunTimeDir":
        dir_mapping = {
            "logs_dir": "logs",
            "data_dir": "data",
            "tests_dir": "test",
            "artifacts_dir": "artifacts",
            "docs_dir": "docs",
        }

        for attr, name in dir_mapping.items():
            if getattr(self, attr) is None:
                setattr(self, attr, self.base_dir / name)
            getattr(self, attr).mkdir(exist_ok=True, parents=True)

        return self

    @model_validator(mode="after")
    def create_sub_runtime_dir(self) -> "RunTimeDir":
        sub_dir_mapping = {
            "processed_data_dir": self.data_dir / "processed",
            "raw_data_dir": self.data_dir / "raw_data_dir",
            "test_data_dir": self.data_dir / "test_data",
        }

        for attr, name in sub_dir_mapping.items():
            if getattr(self, attr) is None:
                setattr(self, attr, name)
            getattr(self, attr).mkdir(exist_ok=True, parents=True)

        return self


if __name__ == "__main__":
    s = RunTimeDir()
    print(s.model_dump())
