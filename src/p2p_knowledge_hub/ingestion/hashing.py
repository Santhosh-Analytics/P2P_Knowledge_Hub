import hashlib
from hashlib import sha256
from pathlib import Path
from p2p_knowledge_hub.exceptions.base import DocumentException, FileOperationError, FileMissingError, FilePermissionError,InvalidPathError, FileReadError, HashingError, DirectoryError
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.logging_config import LogSettings
log_settings = LogSettings()
log = AppLogger(log_settings).get_logger(__name__)


def compute_sha256(file_path: Path) -> sha256:
    if not file_path.exists():
        log.error(f"Path does not exist: {file_path}")
        raise FileMissingError(f"Path does not exist. {file_path}")
    elif file_path.is_dir():
        log.error(f"Expected a file path, but got a directory: {file_path}")
        raise InvalidPathError(f"Expected a file path, but got a directory: {file_path}")
    elif file_path.is_file():
        try:
            with open(file_path, "rb") as f:
                digest = hashlib.file_digest(f, "sha256")
            return digest.hexdigest()

        except FileNotFoundError as e:
            log.error(f"File disappeared during read: {file_path}: {e}")
            raise FileMissingError(f"Path does not exist. {file_path}")
        except PermissionError as e:
            log.error(f"Permission denied reading {file_path}: {e}")
            raise FilePermissionError(message=f"Unable to read. Access denied. {e}")

        except (OSError, IOError) as e:
            log.error(f"I/O error reading {file_path}: {e}")
            raise FileReadError(f"Unable to read the file {e}")


if __name__ == "__main__":
    # ss = compute_sha256(Path("/tmp/hash_permission_test"))
    ss = compute_sha256(Path("/home/san/.config/ggVG"))
    print(ss)
