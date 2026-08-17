from p2p_knowledge_hub.services.rag_pipeline_service import RAGPipelineService
from p2p_knowledge_hub.generation.generation_service import GenerationService
from p2p_knowledge_hub.generation.ollama import OllamaGeneration
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)


def main():
    query = "Advance Payment Workflow"
    retrieval = RetrievalPipelineService()
    generation_service = GenerationService()
    generator = OllamaGeneration("qwen3:1.7b")
    pipe = RAGPipelineService(
        retrieval_service=retrieval,
        generation_service=generation_service,
        generator=generator,
    )

    hybrid = retrieval.hybrid_retriever
    result = pipe.answer(query=query, candidate=hybrid, candidate_k=20, top_k=8)

    print(result)


if __name__ == "__main__":
    main()
