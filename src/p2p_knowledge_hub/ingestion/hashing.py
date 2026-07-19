import hashlib
from pathlib import Path
from p2p_knowledge_hub.exceptions.base import DocumentException


def compute_sha256(file_path: Path) -> str:
    if file_path.is_file():
        try:
            with open(file_path, "rb") as f:
                digest = hashlib.file_digest(f, "sha256")
            return digest.hexdigest()
        except PermissionError as e:
            raise DocumentException(message=f"Unable to read. Access denied. {e}")
    else:
        raise DocumentException("Please provide file Path.")


if __name__ == "__main__":
    # ss = compute_sha256(Path("/tmp/hash_permission_test"))
    ss = compute_sha256(Path("/home/san/annclassification/"))
    print(ss)
