from fastapi import APIRouter, File, Form, UploadFile
from typing import Annotated
from p2p_knowledge_hub.models.document import (
    BusinessProcess,
    SourceDocumentKey,
    SourceSystem,
    Department,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("")
async def create_file(
    file: Annotated[UploadFile, File()],
    source_system: Annotated[SourceSystem, Form()],
    business_process: Annotated[BusinessProcess, Form()],
    department: Annotated[Department, Form()],
    source_document_key: Annotated[SourceDocumentKey, Form()],
    uploaded_by: Annotated[str, Form()],
):
    file_bytes = await file.read()
    result = await pipeline.process_upload(
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

    return result
