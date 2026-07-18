from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from p2p_knowledge_hub.models.document import tz_aware_time


class LogLevel(str, Enum):
    DEBUG = ("debug",)
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSettings(BaseSettings):
    log_to_file: bool = Field(default=True)
    log_to_console: bool = Field(default=True)
    capturewarnings: bool = True
    rich_tracebacks: bool = False

    log_file_handler: RotatingFileHandler
    log_console_handler: RichHandler
    log_level: LogLevel = Field(default=LogLevel.INFO)

    log_file_location: Path = Field(default=Path())
    log_max_bytes: int = Field(default=5_242_880, ge=3_145_728, le=10_485_760)
    log_backupCount: int = Field(default=5, ge=1, le=15)
    log_file_name: str = Field(default_factory=lambda: f"{tz_aware_time:%Y_%m_%d}.log")

    log_file_fmt: str = Field(default="%(asctime)s | %(levelname)-8s | %(message)s")
    log_encoding: str = Field(default="UTF-8")
    log_console_fmt: str = Field(default="%(asctime)s | %(levelname)-8s | %(message)s")
    log_date_fmt: str = "%Y-%m-%d %H:%M:%S"

    model_config = SettingsConfigDict(extra="ignore", env_prefix="p2p")


if __name__ == "__main__":
    log = LogSettings()
    print(log.model_dump)
