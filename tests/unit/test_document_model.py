# "./src/p2p_knowledge_hub/models/document.py"
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError
import pytest
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    Department,
    Document,
    MimeType,
    SourceSystem,
    DocumentStatus,
)
from uuid import uuid4


@pytest.fixture
def valid_document_data():
    return {
        "document_group_id": uuid4(),
        "document_id": uuid4(),
        "document_name": "supplier_policy.pdf",
        "source_system": SourceSystem.TALLY,
        "business_process": BusinessProcess.INVOICE,
        "uploaded_by": "san",
        "uploaded_at": datetime.now(),
        "department": Department.PAYMENT,
        "source_uri": "/tmp/supplier_policy.pdf",
        "file_size_bytes": 23,
        "document_version": 1,
        "document_status": DocumentStatus.INDEXED,
        "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
        "mime_type": MimeType.PDF,
        "source_document_key": "SUPPLIER_POLICY_001",
    }


@pytest.mark.parametrize(
    "key, value , expected",
    [
        ("document_name", "supplier_policy.pdf", "supplier_policy.pdf"),
        ("source_system", "SAP", SourceSystem.SAP),
        ("business_process", "SUPPLIER", BusinessProcess.SUPPLIER),
        ("uploaded_by", "admin", "admin"),
        ("department", "VMF", Department.VMF),
        ("source_uri", "/tmp/supplier_policy.pdf", "/tmp/supplier_policy.pdf"),
        ("file_hash", "a" * 64, "a" * 64),
        ("file_size_bytes", 24, 6 * 4),
        ("document_version", 2, 2),
        ("document_status", "indexed", DocumentStatus.INDEXED),
        (
            "file_hash",
            compute_sha256(Path("/home/san/ss.zsh")),
            compute_sha256(Path("/home/san/ss.zsh")),
        ),
        ("mime_type", "application/pdf", MimeType.PDF),
    ],
)
def test_document_creation_success(valid_document_data, key, value, expected):
    valid_document_data[key] = value

    document = Document(**valid_document_data)

    assert getattr(document, key) == expected


@pytest.mark.parametrize(
    "key, value",
    [
        ("document_name", ""),
        ("source_system", "sap"),
        ("business_process", "supplier"),
        ("uploaded_by", ""),
        ("department", "vmf"),
        ("source_uri", ""),
        ("file_hash", "a"),
        ("file_size_bytes", 0),
        ("document_version", 0),
    ],
)
def test_document_creation_validation(valid_document_data, key, value):
    valid_document_data[key] = value

    with pytest.raises(ValidationError) as exc_info:
        Document(**valid_document_data)

    assert any(error["loc"] == (key,) for error in exc_info.value.errors())


def test_document_version_must_be_at_least_one(valid_document_data):
    valid_document_data["document_version"] = 0

    with pytest.raises(ValidationError) as exc_info:
        Document(**valid_document_data)

    errors = exc_info.value.errors()

    assert errors[0]["loc"] == ("document_version",)
    assert "greater than or equal to 1" in errors[0]["msg"]


def test_document_name_cannot_be_empty(valid_document_data):
    valid_document_data["document_name"] = ""
    with pytest.raises(ValidationError) as exc_info:
        Document(**valid_document_data)

    errors = exc_info.value.errors()

    assert errors[0]["loc"] == ("document_name",)
    assert "String should have at least 1 character" in errors[0]["msg"]
