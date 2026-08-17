from p2p_knowledge_hub.core.timing import latency_decorator
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.reranker.base_reranker import BaseReranker
from sentence_transformers import CrossEncoder


class CrossEncoderReranker(BaseReranker):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = CrossEncoder(model_name)

    @latency_decorator
    def rerank(
        self, query: str, retrieved: list[RetrievedChunk], top_k: int
    ) -> list[RetrievedChunk]:
        pairs: list[tuple[str, str]] = [
            (query, chunk.chunk.text) for chunk in retrieved
        ]
        scores = self.model.predict(pairs)

        sorted_scores = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        reranked: list[RetrievedChunk] = []
        for index, rerank_score in sorted_scores:
            reranked.append(
                retrieved[index].model_copy(
                    update={"rerank_score": float(rerank_score)}
                )
            )

        return reranked[:top_k]
