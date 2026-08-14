from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)


def main():
    retrieval = RetrievalPipelineService()
    query = "Invoice lifecycl"
    hybrid = retrieval.hybrid_retriever
    dense = retrieval.dense_retriever
    sparse = retrieval.bm25_retriever
    result = retrieval.search(query, hybrid, 20, 10)
    print(result)


if __name__ == "__main__":
    main()
