from p2p_knowledge_hub.lexical_index.base_lexical_index import BaseLexicalIndex
from p2p_knowledge_hub.lexical_index.bm25_index import BM25Index
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever


class BM25Retriever(BaseRetriever):
    def __init__(self, lexical_index: BaseLexicalIndex) -> None:
        self.lexical_index = lexical_index

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return self.lexical_index.search(query=query, top_k=top_k)


# if __name__ == "__main__":
# from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
# from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
# from p2p_knowledge_hub.models.embeddings import DocumentEmbedding
# from p2p_knowledge_hub.models.embeddings.sentence_transformers import (
#     SentenceTransformerEmbedding,
# )
# from p2p_knowledge_hub.models.document import tz_aware_time
#
# from p2p_knowledge_hub.ingestion.markdown_loader import MarkDownLoader
# from p2p_knowledge_hub.ingestion.hashing import compute_sha256
# from uuid import uuid4
# from sentence_transformers import SentenceTransformer
# from p2p_knowledge_hub.models.document import (
#     Document,
#     SourceDocumentKey,
#     SourceSystem,
#     BusinessProcess,
#     Department,
#     DocumentStatus,
#     MimeType,
# )
# from datetime import datetime
# from pathlib import Path
#
# def valid_document_data():
#     return {
#         "document_group_id": uuid4(),
#         "document_id": uuid4(),
#         "document_name": "supplier_policy.pdf",
#         "source_system": SourceSystem.TALLY,
#         "business_process": BusinessProcess.INVOICE,
#         "uploaded_by": "san",
#         "uploaded_at": datetime.now(),
#         "department": Department.FINANCE,
#         # "source_uri": "/home/san/Projects/EnterpriseKnowledgeAssistant_bak/data/raw/Vendor onboarding Policy/SOP Accounts - Payable.pdf",
#         "source_uri": "/home/san/Obsidian/Interview/about.md",
#         "file_size_bytes": 23,
#         "document_version": 1,
#         "document_status": DocumentStatus.INDEXED,
#         "file_hash": compute_sha256(Path("/home/san/ss.zsh")),
#         "mime_type": MimeType.PDF,
#         "source_document_key": SourceDocumentKey.CONTRACTING_POLICY,
#     }
#
# import json
#
# document = Document(**valid_document_data())
# loader = MarkDownLoader().load(document)
# chunks = RecursiveChunker().chunk(loader)
# with open("./chunks.txt", "w", encoding="utf-8") as target:
#     target.write(
#         json.dumps([c.model_dump() for c in chunks], indent=2, default=str)
#     )
#
# embeddings = SentenceTransformerEmbedding(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )
# embed_chunks = embeddings.embed(chunks)
# with open("./embed_chunk.txt", "w", encoding="utf-8") as target:
#     target.write(
#         json.dumps([c.model_dump() for c in embed_chunks], indent=2, default=str)
#     )
#
# print(json.dumps([c.model_dump() for c in embed_chunks], indent=2, default=str))
# query = "Hello there good man!"
#
# bm25_index = BM25Index()
# bm25_index.build(chunks)
# retriever = BM25Retriever(lexical_index=bm25_index)
#
# results = retriever.retrieve(
#     query="Hello there good man!",
#     top_k=5,
# )
