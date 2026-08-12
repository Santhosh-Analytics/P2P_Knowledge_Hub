from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)

retrieval = RetrievalPipelineService()

query = "Invoice lifecycl"

# document_pipeline = DocumentPipelineService()
# retrievel_pipeline = RetrievalPipelineService()
results = retrieval.hybrid_retriever.retrieve(query, 5)

print("XO" * 50)
print(results)
print("XO" * 50)
