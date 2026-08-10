from pydantic import BaseModel
from enum import StrEnum
from p2p_knowledge_hub.models.document_page_chunk import DocumentChunk
import numpy as np


class RetrievalSource(StrEnum):
    bm25 = "BM25"
    dense = "Dense"
    hybrid = "Hybrid"


class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    raw_score: float
    retrieval_source: RetrievalSource
