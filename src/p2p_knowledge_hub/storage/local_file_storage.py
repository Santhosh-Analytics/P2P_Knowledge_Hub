from p2p_knowledge_hub.storage.base_file_storage import BaseFileStorage
from pathlib import Path

from p2p_knowledge_hub.settings.main import get_settings

settings = get_settings()


class LocalFileStorage(BaseFileStorage):
    def store(
        self,
        file: bytes,
        file_name: str,
        dir_path: Path = settings.runtime_dir.raw_data_dir,
    ) -> Path:

        with open(Path(dir_path / file_name), "wb") as f:
            f.write(file)

        return Path(dir_path / file_name)
