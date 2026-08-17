from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.lexical_index.bm25_index import BM25Index
from p2p_knowledge_hub.retrieval.dense_retriever import DenseRetriever
from p2p_knowledge_hub.retrieval.bm25_retriever import BM25Retriever
from p2p_knowledge_hub.retrieval.hybrid_retriever import HybridRetriever
from p2p_knowledge_hub.reranker.cross_encoder_reranker import CrossEncoderReranker
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk

from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
from p2p_knowledge_hub.core.timing import latency_decorator

settings = get_settings()


class RetrievalPipelineService:
    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25_index = BM25Index()
        self.refresh_bm25()

        self.dense_retriever = DenseRetriever(self.vector_store, self.embedding_service)
        self.bm25_retriever = BM25Retriever(self.bm25_index)
        self.hybrid_retriever = HybridRetriever(
            sparse_retriever=self.bm25_retriever, dense_retriever=self.dense_retriever
        )
        self.reranker = CrossEncoderReranker(model_name=settings.reranker.model_name)

    @latency_decorator
    def search(
        self, query: str, candidate: BaseRetriever, candidate_k: int, top_k: int
    ) -> list[RetrievedChunk]:

        retrived = candidate.retrieve(query, candidate_k)

        reranked = self.reranker.rerank(query, retrived, top_k)

        return reranked

    def refresh_bm25(self) -> None:
        chunks = self.vector_store.get_all_chunks()
        self.bm25_index.build(chunks)
