from p2p_knowledge_hub.services.document_pipeline_service import DocumentPipelineService
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)

query = "Invoice lifecycl"

document_pipeline = DocumentPipelineService()
retrievel_pipeline = RetrievalPipelineService()

results_bm25 = retrievel_pipeline.bm25_retriever.retrieve(query, 5)
results_dense = retrievel_pipeline.dense_retriever.retrieve(query, 5)
print("XO" * 50)
print(results_bm25)
print("XO" * 50)
print(results_dense)
