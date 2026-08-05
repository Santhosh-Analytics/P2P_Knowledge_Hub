from p2p_knowledge_hub.vector_store.base_vector_store import BaseVectorStore
from p2p_knowledge_hub.models import DocumentChunk, DocumentEmbedding
from chromadb import Client


class ChromaVectorStore(BaseVectorStore):
    def __init__(self) -> None:
        self.client = Client()
        self.collection = self.client.get_or_create_collection("p2p_docs")

    def upsert(
        self, chunks: list[DocumentChunk], embeddings: list[DocumentEmbedding]
    ) -> None:
        if len(chunks) == len(embeddings):
            ids: list[str] = [str(chunk.chunk_id) for chunk in chunks]
            embed_vectors: list[list[float]] = [
                embed.embeddings for embed in embeddings
            ]
            metadatas: list[dict[str, str | int | float | bool]] = [
                chunk.model_dump(mode="json",exclude={"text",exclude_none=True,}) for chunk in chunks
            ]
            documents: list[str] = [chunk.text for chunk in chunks]

            self.collection.upsert(
                ids=ids,
                embeddings=embed_vectors,
                metadatas=metadatas,
                documents=documents,
            )
