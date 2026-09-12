from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from chromadb import ClientAPI
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)
from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from p2p_knowledge_hub.settings.main import get_settings
from pathlib import Path

settings = get_settings()


def create_retrieval_pipeline() -> RetrievalPipelineService:
    client = chromadb.PersistentClient(
        path=Path(settings.runtime_dir.base_dir / "chroma"),
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    embedding_service = SentenceTransformerEmbedding(
        model_name=settings.embeddings.embedding_model,
        provider=settings.embeddings.model_provider,
    )
    vector_store = ChromaVectorStore(client)

    return RetrievalPipelineService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )
