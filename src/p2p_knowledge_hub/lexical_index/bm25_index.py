from rank_bm25 import BM25Okapi
import numpy as np
from p2p_knowledge_hub.lexical_index.base_lexical_index import BaseLexicalIndex
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.models.retrieved_chunk import RetrievalSource


class BM25Index(BaseLexicalIndex):
    def build(self, chunks: list[DocumentChunk]) -> None:
        self.filtered_tokenized_corpus, self.filtered_chunks = self._tokenize_corpus(
            chunks
        )
        self.bm25_index: BM25Okapi = BM25Okapi(self.filtered_tokenized_corpus)

    def _tokenize_corpus(
        self, chunks: list[DocumentChunk]
    ) -> tuple[list[list[str]], list[DocumentChunk]]:
        self._filtered_chunks: list[DocumentChunk] = []
        self._filtered_tokenized_corpus: list[list[str]] = []

        for chunk in chunks:
            if chunk.text is not None and chunk.text.strip():
                self._filtered_chunks.append(chunk)
                self._filtered_tokenized_corpus.append(self._tokenize(chunk.text))
        return (self._filtered_tokenized_corpus, self._filtered_chunks)

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if not hasattr(self, "bm25_index"):
            raise RuntimeError("BM25 index has not been built")
        tokenized_query = self._tokenize(query)
        scores: np.ndarray = self.bm25_index.get_scores(tokenized_query)
        positive_scores = (
            (idx, score) for idx, score in enumerate(scores) if score > 0
        )

        ranked = sorted(positive_scores, key=lambda x: x[1], reverse=True)
        top_results = ranked[:top_k]

        return [
            RetrievedChunk(
                chunk=self.filtered_chunks[idx],
                raw_score=float(score),
                retrieval_source=RetrievalSource.bm25,
            )
            for idx, score in top_results
        ]

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()
