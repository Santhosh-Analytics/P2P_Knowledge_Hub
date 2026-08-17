from contextlib import asynccontextmanager
from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService
from fastapi import FastAPI


@asynccontextmanager
async def rag_pipeline_lifespan(app: FastAPI):
    print("Application is starting up")
    pipe = RAGPipelineService()
    yield
