from p2p_knowledge_hub.models.retrieved_chunk import RetrievalSource
from fastapi import APIRouter, Depends
from typing import Annotated
from p2p_knowledge_hub.models.generation_result import GenerationResult
from p2p_knowledge_hub.models.api.query_request import QueryRequest
from p2p_knowledge_hub.api.dependencies import get_rag_pipeline
from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService

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
    return pipeline.answer(
        query=query.query,
        retriever=query.retriever,
        candidate_k=query.candidate_k,
        top_k=query.top_k,
    )
