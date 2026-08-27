from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from p2p_knowledge_hub.models.generation_result import GenerationResult
from p2p_knowledge_hub.models.api.query_request import QueryRequest
from p2p_knowledge_hub.api.dependencies import get_rag_pipeline
from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService
from p2p_knowledge_hub.exceptions.chunking_exceptions import NoIndexedChunksError
from rich import print
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.core.logger import AppLogger

settings = get_settings()
_logger = AppLogger(settings.logs).get_logger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["query"],
)


@router.post("", response_model=GenerationResult)
async def query_request(
    query: QueryRequest,
    pipeline: Annotated[
        RAGPipelineService,
        Depends(get_rag_pipeline),
    ],
) -> GenerationResult:
    try:
        return pipeline.answer(
            query=query.query,
            retriever=query.retriever,
            candidate_k=query.candidate_k,
            top_k=query.top_k,
        )
    except NoIndexedChunksError as exc:
        _logger.warning(
            f"[bold red blink]No chunks indexed: {exc}",
            extra={"markup": True},
        )
        raise HTTPException(
            status_code=409, detail=f"No chunks indexed: {exc}"
        ) from exc
