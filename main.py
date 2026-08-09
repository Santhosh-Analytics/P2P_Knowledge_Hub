from rich import print
from pathlib import Path
from p2p_knowledge_hub.ingestion.markdown_loader import MarkDownLoader
from p2p_knowledge_hub.services.ingestion_service import (
    MetadataCollector,
    IngestionService,
)
from p2p_knowledge_hub.exceptions.base import FileMissingError
from p2p_knowledge_hub.services.indexing_services import IndexingService
from p2p_knowledge_hub.chunking.recursive_chunker import RecursiveChunker
from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from p2p_knowledge_hub.lexical_index.bm25_index import BM25Index
from p2p_knowledge_hub.retrieval.bm25_retriever import BM25Retriever
from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore
import json
from chromadb.config import Settings as ChromaSettings
import chromadb

chroma_client = chromadb.PersistentClient(
    path="./chroma", settings=ChromaSettings(anonymized_telemetry=False)
)
user_input = str(input())
file_path = Path(user_input)
try:
    document = MetadataCollector().collect_document(Path(file_path))
except FileMissingError as exc:
    print(f"[bold red blink]ERROR: Path does not exist. {user_input}")
    print()
    print(f"[bold red blink]{exc}")
except ValueError as exc:
    print(f"[bold red blink]ERROR: Please select option using number. {user_input}")
    print()
    print(f"[bold red blink]{exc}")

# loader = MarkDownLoader()
# metadata_injector = IngestionService()
# metadata_injector.ingestion_service(document)
#
# loaded_document = loader.load(document)
# chunker = RecursiveChunker()
# chunks = chunker.chunk(loaded_document)
#
# embeddings = SentenceTransformerEmbedding(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )
# vector_store = ChromaVectorStore(client=chroma_client)
#
# index_service = IndexingService(embeddings, vector_store)
# embed_chunks = index_service.index(chunks)
#
# bm25_index = BM25Index()
# bm25_index.build(chunks)
# bm25_retriever = BM25Retriever(lexical_index=bm25_index)
# results = bm25_retriever.retrieve(
#     query="linear regression cost function",
#     top_k=5,
# )
#
# for rank, result in enumerate(results, start=1):
#     print(rank)
#     print(result.score)
#     print(result.chunk.title)
#     print(result.chunk.section)
#     print(result.chunk.text)
