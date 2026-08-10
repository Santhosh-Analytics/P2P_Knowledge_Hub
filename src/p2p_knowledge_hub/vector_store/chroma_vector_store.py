from uuid import UUID

from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from chromadb.api import ClientAPI
from chromadb.api.types import Embedding, Metadata
from typing import cast
from p2p_knowledge_hub.models.retrieved_chunk import RetrievalSource, RetrievedChunk

settings = get_settings()
_log = AppLogger(settings.logs).get_logger(__name__)


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, client: ClientAPI) -> None:
        self.client = client
        self.collection = self.client.get_or_create_collection("p2p_docs")

    def upsert(
        self, chunks: list[DocumentChunk], embeddings: list[DocumentEmbedding]
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Expected {len(chunks)} chunks but received {len(embeddings)} embeddings."
            )

        ids: list[str] = []
        embed_vectors: list[Embedding] = []
        metadatas: list[Metadata] = []
        documents: list[str] = []

        for chunk, embedding in zip(chunks, embeddings):
            text = chunk.text
            if chunk.chunk_id != embedding.chunk_id:
                raise ValueError(
                    f"Chunk ID mismatch: chunk={chunk.chunk_id}, embedding={embedding.chunk_id}"
                )
            ids.append(str(chunk.chunk_id))
            embed_vectors.append(cast(Embedding, embedding.embeddings))
            metadatas.append(
                chunk.model_dump(
                    mode="json",
                    exclude={"text"},
                    exclude_none=True,
                )
            )

            if text is None or not text.strip():
                raise ValueError(f"Chunk {chunk.chunk_id} has empty text")
            documents.append(text)

        self.collection.upsert(
            ids=ids,
            embeddings=embed_vectors,
            metadatas=metadatas,
            documents=documents,
        )

    def search(self, query_embeddings: list[float], top_k: int) -> list[RetrievedChunk]:
        retrieved = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        results: list[RetrievedChunk] = []

        for chunk_id, text, metadata, score in zip(
            retrieved["ids"][0],
            retrieved["documents"][0],
            retrieved["metadatas"][0],
            retrieved["distances"][0],
        ):
            metadata = dict(metadata)
            metadata.pop("chunk_id", None)

            document_chunk = DocumentChunk(
                chunk_id=UUID(chunk_id), text=text, **metadata
            )

            results.append(
                RetrievedChunk(
                    chunk=document_chunk,
                    raw_score=float(score),
                    retrieval_source=RetrievalSource.dense,
                )
            )

        return results

    def get_all_chunks(self) -> list[DocumentChunk]:
        results = self.collection.get()

        chunks: list[DocumentChunk] = []

        for chunk_id, text, metadata in zip(
            results["ids"], results["documents"], results["metadatas"]
        ):
            metadata = dict(metadata)  # make a copy
            metadata.pop("chunk_id", None)

            chunk = DocumentChunk(chunk_id=UUID(chunk_id), text=text, **metadata)
            chunks.append(chunk)

        return chunks
