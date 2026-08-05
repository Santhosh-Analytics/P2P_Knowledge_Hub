from sentence_transformers import SentenceTransformer
from p2p_knowledge_hub.embeddings.base_embedding import BaseEmbeddingService
from p2p_knowledge_hub.exceptions.chunking_exceptions import P2PHubException
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
from p2p_knowledge_hub.models.document import tz_aware_time

settings = get_settings()
_log = AppLogger(settings.logs).get_logger(__name__)


class SentenceTransformerEmbedding(BaseEmbeddingService):
    def __init__(self, model_name: str, provider: str = "SentenceTransformer") -> None:
        self.model_name = model_name
        self.provider = provider
        self.model = SentenceTransformer(model_name)

    def embed(self, chunks: list[DocumentChunk]) -> list[DocumentEmbedding]:
        for chunk in chunks:
            if not chunk.text.strip():
                raise ValueError(f"Chunk {chunk.chunk_id} contains empty text")

        document_embedding: list[DocumentEmbedding] = []
        embed_text = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(embed_text, normalize_embeddings=True)

        for embed_chunk, chunk in zip(embeddings, chunks):
            document_embedding.append(
                DocumentEmbedding(
                    chunk_id=chunk.chunk_id,
                    embeddings=embed_chunk.tolist(),
                    embedding_provider=self.provider,
                    embedding_model=self.model_name,
                    created_at=tz_aware_time(),
                    embedding_dimension=len(embed_chunk),
                )
            )
        return document_embedding


if __name__ == "__main__":
    from p2p_knowledge_hub.ingestion.markdown_loader import MarkDownLoader
    from p2p_knowledge_hub.ingestion.hashing import compute_sha256
    from uuid import uuid4
    from p2p_knowledge_hub.models.document import (
        Document,
        SourceDocumentKey,
        SourceSystem,
        BusinessProcess,
        Department,
        DocumentStatus,
        MimeType,
    )
    from datetime import datetime
    from pathlib import Path

    def valid_document_data():
        return {
            "document_group_id": uuid4(),
            "document_id": uuid4(),
            "document_name": "supplier_policy.pdf",
            "source_system": SourceSystem.TALLY,
            "business_process": BusinessProcess.INVOICE,
            "uploaded_by": "san",
            "uploaded_at": datetime.now(),
            "department": Department.FINANCE,
            # "source_uri": "/home/san/Projects/EnterpriseKnowledgeAssistant_bak/data/raw/Vendor onboarding Policy/SOP Accounts - Payable.pdf",
            "source_uri": "/home/san/Obsidian/Interview/about.md",
            "file_size_bytes": 23,
            "document_version": 1,
            "document_status": DocumentStatus.INDEXED,
            "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
            "mime_type": MimeType.PDF,
            "source_document_key": SourceDocumentKey.CONTRACTING_POLICY,
        }

    import json

    document = Document(**valid_document_data())
    loader = MarkDownLoader().load(document)
    chunks = RecursiveChunker().chunk(loader)
    with open("./chunks.txt", "w", encoding="utf-8") as target:
        target.write(
            json.dumps([c.model_dump() for c in chunks], indent=2, default=str)
        )

    embeddings = SentenceTransformerEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    embed_chunks = embeddings.embed(chunks)
    with open("./embed_chunk.txt", "w", encoding="utf-8") as target:
        target.write(
            json.dumps([c.model_dump() for c in embed_chunks], indent=2, default=str)
        )

    print(json.dumps([c.model_dump() for c in embed_chunks], indent=2, default=str))
