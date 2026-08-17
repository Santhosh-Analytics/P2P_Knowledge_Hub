from pydantic_settings import SettingsConfigDict, BaseSettings


class GenerationSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="P2P_")
    model_name: str
