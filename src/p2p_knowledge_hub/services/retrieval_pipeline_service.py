from pathlib import Path


from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.lexical_index.bm25_index import BM25Index
from p2p_knowledge_hub.retrieval.dense_retriever import DenseRetriever
from p2p_knowledge_hub.retrieval.bm25_retriever import BM25Retriever


settings = get_settings()


class RetrievalPipelineService:
    def __init__(self) -> None:
        self.embedding_service = SentenceTransformerEmbedding(
            model_name=settings.embeddings.embedding_model
        )
        self.chroma_client = chromadb.PersistentClient(
            path=Path(settings.runtime_dir.base_dir / "chroma"),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.vector_store = ChromaVectorStore(client=self.chroma_client)
        self.bm25_index = BM25Index()
        chunks = self.vector_store.get_all_chunks()
        self.bm25_index.build(chunks)

        self.dense_retriever = DenseRetriever(self.vector_store, self.embedding_service)
        self.bm25_retriever = BM25Retriever(self.bm25_index)
