from abc import abstractmethod, ABC
from pathlib import Path


class BaseFileStorage(ABC):
    @abstractmethod
    def store(
        self,
        file: bytes,
        file_name: str,
        dir_path: Path,
    ) -> Path:
        raise NotImplementedError
