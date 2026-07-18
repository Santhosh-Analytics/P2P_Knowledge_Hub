import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from p2p_knowledge_hub import settings
from p2p_knowledge_hub.settings import LogSettings


class AppLogger:
    def __init__(self, settings: LogSettings) -> None:
        self.settings = settings
        if self.settings.capturewarnings:
            logging.captureWarnings(True)

    def make_file_handler(self) -> RotatingFileHandler:
        _handlers = RotatingFileHandler(
            filename=self.settings.log_file_name,
            maxBytes=self.settings.log_max_bytes,
            backupCount=LogSettings.log_backupCount,
            encoding=LogSettings.log_encoding,
        )
        fmt = logging.Formatter(
            self.settings.log_file_fmt, datefmt=self.settings.log_date_fmt
        )
        _handlers.format(fmt)
        _handlers.setLevel(self.settings.log_level)

        return _handlers

    def make_console_handler(self):
        _handlers = RichHandler(
            level=self.settings.log_level,
            show_level=True,
            show_time=True,
            show_path=True,
            rich_tracebacks=self.settings.rich_tracebacks,
        )
        return _handlers

    def get_logger(self, name: str | None = None) -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        logger.setLevel(self.settings.log_level)
        logger.propagate = False
        if self.settings.log_to_console:
            logger.addHandler(self.make_console_handler())
        if self.settings.log_to_file:
            logger.addHandler(self.make_file_handler())

        return logger


if __name__ == "__main__":
    p2p_logger = AppLogger(settings=LogSettings())
    p2p_logger.get_logger("San")
