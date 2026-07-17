import hashlib
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")
    return digest.hexdigest()
