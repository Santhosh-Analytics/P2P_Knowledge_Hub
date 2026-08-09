from fastapi import APIRouter, File, Form, UploadFile
from typing import Annotated
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    SourceDocumentKey,
    SourceSystem,
    Department,
)
from p2p_knowledge_hub.models.api.document_upload import DocumentUploadResponse
from p2p_knowledge_hub.services.document_pipeline_service import DocumentPipelineService
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings


# settings = get_settings()
# _log = AppLogger(settings).get_logger(__name__)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

pipeline = DocumentPipelineService()


@router.post("", response_model=DocumentUploadResponse)
async def create_file(
    file: Annotated[UploadFile, File()],
    source_system: Annotated[SourceSystem, Form()],
    business_process: Annotated[BusinessProcess, Form()],
    department: Annotated[Department, Form()],
    source_document_key: Annotated[SourceDocumentKey, Form()],
    uploaded_by: Annotated[str, Form()],
):
    file_bytes = await file.read()
    document = await pipeline.process_upload(
        file_bytes=file_bytes,
        file_name=file.filename,
        file_size=file.size,
        content_type=file.content_type,
        source_system=source_system,
        business_process=business_process,
        department=department,
        source_document_key=source_document_key,
        uploaded_by=uploaded_by,
    )
    return document
