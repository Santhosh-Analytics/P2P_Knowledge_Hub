from enum import Enum
from uuid import uuid4

from p2p_knowledge_hub.models.db.sessions import SessionManager
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    SourceDocumentKey,
    Department,
    Document,
    DocumentStatus,
    SourceSystem,
    tz_aware_time,
)
from p2p_knowledge_hub.settings.main import get_settings

# from p2p_knowledge_hub.exceptions.ingestion import P2P_IngessionError
from p2p_knowledge_hub.ingestion.hashing import compute_sha256
from pathlib import Path
import mimetypes

from p2p_knowledge_hub.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork


class MetadataCollector:
    def choose_enum(self, enum_class: Enum) -> Enum.value:
        values = list(enum_class)
        for number, item in enumerate(values, start=1):
            print(number, item.value)
        selected_number = int(input("Select an option: "))
        return values[selected_number - 1]

    def collect_document(self, file_path: Path) -> Document:
        department = self.choose_enum(Department)
        business_process = self.choose_enum(BusinessProcess)
        source_system = self.choose_enum(SourceSystem)
        source_document_key = self.choose_enum(SourceDocumentKey)
        # self.document_status = self.choose_enum(DocumentStatus)
        mime_type = mimetypes.guess_type(file_path)[0]

        document = Document(
            file_hash=compute_sha256(file_path),
            document_id=uuid4(),
            document_group_id=uuid4(),
            document_name=file_path.name,
            department=department,
            business_process=business_process,
            source_system=source_system,
            # self.document_version = self.document_version + 1 ,
            uploaded_at=tz_aware_time(),
            uploaded_by=str(input("Enter your email: ")),
            file_size_bytes=file_path.lstat()[6],
            mime_type=str(mime_type),
            source_document_key=source_document_key,
            source_uri=str(file_path),
        )
        return document


class IngestionService:
    def ingestion_service(self, document: Document):
        with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
            exact_duplicate = uow.document.find_exact_duplicate(
                document.source_system,
                document.business_process,
                document.department,
                document.file_hash,
                document.source_document_key,
            )

            if exact_duplicate is not None:
                print(
                    f"The provided document : {exact_duplicate.document_name} is already avilable in the record with id {exact_duplicate.document_id}"
                )

            duplicate = uow.document.find_latest_version(
                document.source_system,
                document.business_process,
                document.department,
                document.source_document_key,
            )

            if duplicate is None:
                uow.document.add(document)
                uow.commit()


if __name__ == "__main__":
    data = MetadataCollector().collect_document(
        file_path=Path("/home/san/Documents/all_packages.txt")
    )

    print(IngestionService().ingestion_service(data))

    # source_document_key: Mapped[str] = mapped_column(String(100), nullable=False)
    # mime_type: Mapped[MimeType] = mapped_column(
    #     Enum(MimeType, name="mime_type_enum"), nullable=False
    # )
    # source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    #
    #
    #
    #
