from p2p_knowledge_hub.services.document_pipeline_service import DocumentPipelineService

from p2p_knowledge_hub.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)

from p2p_knowledge_hub.vector_store.chroma_vector_store import ChromaVectorStore
from chromadb.api import ClientAPI

vector_store = ChromaVectorStore(client=ClientAPI)
embeddings = SentenceTransformerEmbedding(
    "sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers"
)
pipe = DocumentPipelineService(embedding_service=embeddings, vector_store=vector_store)

pipe.chunker.chunk()
