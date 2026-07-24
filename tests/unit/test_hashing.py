from string import hexdigits

import pytest
from p2p_knowledge_hub.exceptions.base import FileMissingError, InvalidPathError
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from pathlib import Path
import hashlib


def test_compute_sha256_given_directory_raises_invalid_path(tmp_path):
    with pytest.raises(InvalidPathError):
        compute_sha256(tmp_path)


def test_compute_sha256_given_missing_file_raises_file_missing(tmp_path):
    with pytest.raises(FileMissingError):
        compute_sha256(Path(tmp_path / "ss.text"))


def test_compute_sha256_given_valid_file_returns_expected_hash(tmp_path):
    with open(tmp_path / "test.txt", "wb") as f:
        f.write(b"hello world")

    assert (
        compute_sha256(tmp_path / "test.txt")
        == hashlib.sha256(b"hello world").hexdigest()
    )
