from contextlib import asynccontextmanager
from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService
from fastapi import FastAPI, Request
from p2p_knowledge_hub.generation.generation_service import GenerationService
from p2p_knowledge_hub.generation.ollama import OllamaGeneration
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)
from p2p_knowledge_hub.settings.main import get_settings

from p2p_knowledge_hub.services.document_pipeline_service import DocumentPipelineService
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore

settings = get_settings()


@asynccontextmanager
async def pipeline_lifespan(app: FastAPI):
    embedding_service = SentenceTransformerEmbedding(
        model_name=settings.embeddings.embedding_model
    )
    chroma_client = chromadb.PersistentClient(
        path=Path(settings.runtime_dir.base_dir / "chroma"),
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    vector_store = ChromaVectorStore(client=chroma_client)
    retrieval = RetrievalPipelineService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )
    generation = GenerationService()
    generator = OllamaGeneration(model_name=settings.generation.model_name)

    app.state.rag_pipeline = RAGPipelineService(
        retrieval_service=retrieval,
        generation_service=generation,
        generator=generator,
    )
    app.state.document_pipeline = DocumentPipelineService(
        embedding_service, vector_store
    )

    yield


def get_document_pipeline(request: Request) -> DocumentPipelineService:
    return request.app.state.document_pipeline


def get_rag_pipeline(request: Request) -> RAGPipelineService:
    return request.app.state.rag_pipeline
