# "./src/p2p_knowledge_hub/models/document.py"
from pydantic import ValidationError
import pytest
from p2p_knowledge_hub.models.document import Document, SourceSystem
from uuid import uuid4


@pytest.fixture
def valid_document_data():
    return {
        "document_group_id": uuid4(),
        "document_id": uuid4(),
        "document_name": "supplier_policy.pdf",
        "source_system": "SAP",
        "business_process": "SUPPLIER",
        "uploaded_by": "san",
        "department": "VMF",
        "source_uri": "/tmp/supplier_policy.pdf",
        "file_hash": "a" * 64,
        "file_size_bytes": 23,
        "document_version": 1,
    }


@pytest.mark.parametrize(
    "key, value",
    [
        ("uploaded_by", "san"),
        ("document_name", "supplier_policy.pdf"),
        ("source_system", "SAP"),
        ("business_process", "SUPPLIER"),
        ("uploaded_by", "san"),
        ("department", "VMF"),
        ("source_uri", "/tmp/supplier_policy.pdf"),
        ("file_hash", "a" * 64),
        ("file_size_bytes", 23),
        ("document_version", 1),
    ],
)
def test_document_creation_success(valid_document_data, key, value):
    valid_document_data[key] = value

    document = Document(**valid_document_data)

    assert getattr(document, key) == value


def test_document_version_must_be_at_least_one(valid_document_data):
    valid_document_data["document_version"] = 0

    with pytest.raises(ValidationError) as exc_info:
        Document(**valid_document_data)

    errors = exc_info.value.errors()

    assert errors[0]["loc"] == ("document_version",)
    assert "greater than or equal to 1" in errors[0]["msg"]


def test_document_file_hash_length():

    pass


def test_document_name_cannot_be_empty():
    pass
