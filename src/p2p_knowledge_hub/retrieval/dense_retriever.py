from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService


class DenseRetriever(BaseRetriever):
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_service: BaseEmbeddingService,
    ) -> None:

        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        query_embedding: list[float] = self.embedding_service.embed_query(query)
        return self.vector_store.search(query_embedding, top_k)
