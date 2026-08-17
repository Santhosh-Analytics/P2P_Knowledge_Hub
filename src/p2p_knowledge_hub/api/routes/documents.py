from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService
from fastapi import APIRouter, File, Form, UploadFile, Depends
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
from p2p_knowledge_hub.api.dependencies import get_rag_pipeline

from p2p_knowledge_hub.api.dependencies import get_document_pipeline

# settings = get_settings()
# _log = AppLogger(settings).get_logger(__name__)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("", response_model=DocumentUploadResponse)
async def create_file(
    file: Annotated[UploadFile, File()],
    source_system: Annotated[SourceSystem, Form()],
    business_process: Annotated[BusinessProcess, Form()],
    department: Annotated[Department, Form()],
    source_document_key: Annotated[SourceDocumentKey, Form()],
    uploaded_by: Annotated[str, Form()],
    document_pipeline: Annotated[
        DocumentPipelineService, Depends(get_document_pipeline)
    ],
    rag_pipeline: Annotated[RAGPipelineService, Depends(get_rag_pipeline)],
):
    file_bytes = await file.read()
    document = await document_pipeline.process_upload(
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
    rag_pipeline.retrieval_service.refresh_bm25()

    return document
