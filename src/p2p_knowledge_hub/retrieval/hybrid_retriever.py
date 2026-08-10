from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)
from uuid import UUID

settings = get_settings()


class HybridRetriever(BaseRetriever):
    def __init__(self) -> None:
        self.pipeline = RetrievalPipelineService()

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        sparse_results = self.pipeline.bm25_retriever.retrieve(query=query, top_k=top_k)
        dense_results = self.pipeline.dense_retriever.retrieve(query=query, top_k=top_k)
        return self._reciprocal_rank_fusion(sparse_results, dense_results)

    def _reciprocal_rank_fusion(
        self,
        sparse_results: list[RetrievedChunk],
        dense_results: list[RetrievedChunk],
        k: int = 60,
    ) -> list[RetrievedChunk]:

        scores: dict[UUID, float] = {}

        for rank, result in enumerate(dense_results):
            chunk_id = result.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)

        for rank, result in enumerate(sparse_results):
            chunk_id = result.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)

        fused_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        fused_results: list[RetrievedChunk] = []
        for cid, _ in fused_ids:
            candidate = next(
                (r for r in dense_results if r.chunk.chunk_id == cid),
                next(r for r in sparse_results if r.chunk.chunk_id == cid),
            )
            fused_results.append(candidate)
        return fused_results
