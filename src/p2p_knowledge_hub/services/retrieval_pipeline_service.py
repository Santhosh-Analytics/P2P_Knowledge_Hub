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
from p2p_knowledge_hub.retrieval.hybrid_retriever import HybridRetriever
from p2p_knowledge_hub.reranker.cross_encoder_reranker import CrossEncoderReranker
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk

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
        self.hybrid_retriever = HybridRetriever(
            sparse_retriever=self.bm25_retriever, dense_retriever=self.dense_retriever
        )
        self.reranker = CrossEncoderReranker(model_name=settings.reranker.model_name)

    def search(
        self, query: str, candidate: BaseRetriever, candidate_k: int, top_k: int
    ) -> list[RetrievedChunk]:

        retrived = candidate.retrieve(query, candidate_k)

        reranked = self.reranker.rerank(query, retrived, top_k)

        return reranked
