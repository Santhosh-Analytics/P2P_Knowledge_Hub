from p2p_knowledge_hub.models.retrieved_chunk import RetrievalSource, RetrievedChunk
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from uuid import UUID
from pathlib import Path


from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from p2p_knowledge_hub.lexical_index.bm25_index import BM25Index
from p2p_knowledge_hub.retrieval.dense_retriever import DenseRetriever
from p2p_knowledge_hub.retrieval.bm25_retriever import BM25Retriever


settings = get_settings()


class HybridRetriever(BaseRetriever):
    def __init__(
        self,
        sparse_retriever: BaseRetriever,
        dense_retriever: BaseRetriever,
    ) -> None:
        self.sparse_retriever = sparse_retriever
        self.dense_retriever = dense_retriever

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        sparse_results = self.sparse_retriever.retrieve(query, top_k)
        dense_results = self.dense_retriever.retrieve(query=query, top_k=top_k)

        return self._reciprocal_rank_fusion(sparse_results, dense_results)[:top_k]

    def _reciprocal_rank_fusion(
        self,
        sparse_results: list[RetrievedChunk],
        dense_results: list[RetrievedChunk],
        k: int = 60,
    ) -> list[RetrievedChunk]:

        scores: dict[UUID, float] = {}
        result_lookup: dict[UUID, RetrievedChunk] = {}

        for rank, result in enumerate(dense_results, start=1):
            chunk_id = result.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)
            result_lookup[chunk_id] = result

        for rank, result in enumerate(sparse_results, start=1):
            chunk_id = result.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)
            result_lookup[chunk_id] = result

        fused_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        retrieved: list[RetrievedChunk] = []

        for chunk_id, fused_score in fused_ids:
            retrieved.append(
                RetrievedChunk(
                    chunk=result_lookup.get(chunk_id).chunk,
                    raw_score=fused_score,
                    retrieval_source=RetrievalSource.hybrid,
                )
            )

        return retrieved
