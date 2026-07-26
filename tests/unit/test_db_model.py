import pytest
from p2p_knowledge_hub.models.db.document import DocumentRecord
from enum import Enum

from p2p_knowledge_hub.models.document import SourceSystem


def test_document_table_name():
    assert DocumentRecord.__tablename__ == "documents"


def test_document_id_is_primary_key():
    column = DocumentRecord.__table__.columns["document_id"]

    assert column.primary_key is True


def test_document_name_is_required():
    column = DocumentRecord.__table__.columns["document_name"]

    assert column.nullable is False
    assert column.type.length == 255


@pytest.mark.parametrize(
    "column_name",
    [
        "document_id",
        "document_group_id",
        "document_name",
        "department",
        "source_system",
        "source_document_key",
        "business_process",
        "file_hash",
        "document_status",
        "document_version",
        "uploaded_at",
        "file_size_bytes",
        "uploaded_by",
        "mime_type",
        "source_uri",
    ],
)
def test_required_columns_are_not_nullable(column_name):
    column = DocumentRecord.__table__.columns[column_name]

    assert column.nullable is False
