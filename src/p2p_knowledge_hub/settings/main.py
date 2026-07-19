from functools import lru_cache
from p2p_knowledge_hub.settings import ExceptionSettings, LogSettings, RunTimeDir


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
    app_name: str = Field(default="P2P Knowledge Hub", min_length=4)
    runtime_dir: RunTimeDir = Field(default_factory=RunTimeDir)
    logs: LogSettings = Field(default_factory=LogSettings)
    exceptions: ExceptionSettings = Field(default_factory=ExceptionSettings)
    # chunks
    model_config = SettingsConfigDict(
        toml_file=_base_dir / "config.toml",
        env_prefix="p2p_",
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
            TomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
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
