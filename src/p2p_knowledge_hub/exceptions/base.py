from types import TracebackType
import traceback
from pathlib import Path
from p2p_knowledge_hub.settings.exceptions import ExceptionSettings


class P2PHubException(Exception):
    settings = ExceptionSettings()

    def __init__(
        self,
        message: str | None = None,
        error_code: str = "P2P_HUB_ERROR",
        tb: TracebackType | None = None,
        exc_type: str | None = None,
    ) -> None:
        self.message = message or self.settings.default_error_message
        self.error_code = error_code
        self.traceback_info = (
            self._extract(tb, exc_type)
            if self.settings.include_traceback_in_logs
            else None
        )
        super().__init__(self.message)

    def _extract(
        self, tb: TracebackType | None = None, exc_type: str | None = None
    ) -> str | None:
        if tb is None:
            return None

        extracted = traceback.extract_tb(tb)
        if not extracted:
            return None
        frame = extracted[-1]
        return f"{exc_type} at {Path(frame.filename).name} line {frame.lineno}"

    def __str__(self) -> str:
        if self.traceback_info and self.settings.debug_mode:
            return f"{self.message} \n {self.traceback_info}"
        return f"{self.message}"


class DocumentException(P2PHubException):
    pass

class FileOperationError(P2PHubException):
    pass

class FileMissingError(FileOperationError):
    pass

class FilePermissionError(FileOperationError):
    pass

class InvalidPathError(FileOperationError):
    pass

class DirectoryError(FileOperationError):
    pass


class FileReadError(FileOperationError):
    pass

class HashingError(P2PHubException):
    pass
