from p2p_knowledge_hub.composition.retrieval import create_retrieval_pipeline

query = "New Supplier setup process?"

pipe = create_retrieval_pipeline()


retrieved = pipe.hybrid_retriever.retrieve(query, 20)
reranked = pipe.reranker.rerank(query, retrieved, 10)


for rank, chunk in enumerate(reranked, start=1):
    print("=+" * 25)
    print(f"Rank: {rank}")
    print("-*" * 25)
    print(f"Chunk ID: {chunk.chunk.chunk_id}")
    print("-*" * 25)
    print(f"Document ID: {chunk.chunk.document_id}")
    print("-*" * 25)
    print(f"Section: {chunk.chunk.section}")
    print("-*" * 25)
    print(f"Chunk: {chunk.chunk.text}")
    print("-*" * 25)
    print(f"Retrieval Source: {chunk.retrieval_source}")
    print("-*" * 25)
    print(f"Rerank Score: {chunk.rerank_score}")
