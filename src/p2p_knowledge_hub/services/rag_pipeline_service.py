from p2p_knowledge_hub.core.timing import latency_decorator
from p2p_knowledge_hub.models.generation_result import GenerationResult
from p2p_knowledge_hub.retrieval.base_retriever import BaseRetriever
from p2p_knowledge_hub.generation.base_generator import BaseGenerator
from p2p_knowledge_hub.generation.generation_service import GenerationService
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)
from p2p_knowledge_hub.models.generation_citation import GenerationCitation


class RAGPipelineService:
    def __init__(
        self,
        retrieval_service: RetrievalPipelineService,
        generation_service: GenerationService,
        generator: BaseGenerator,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.generator = generator

    @latency_decorator
    def answer(
        self, query: str, candidate: BaseRetriever, candidate_k: int, top_k: int
    ) -> GenerationResult:
        reranked_chunks = self.retrieval_service.search(
            query=query, candidate=candidate, candidate_k=candidate_k, top_k=top_k
        )
        unique_ids = self.generation_service.unique_documents(
            reranked_documents=reranked_chunks
        )
        documents = self.generation_service.get_document_record(ids=unique_ids)
        generation_context = self.generation_service.build_context(
            reranked_chunks, documents
        )
        response = self.generator.generate(query=query, contexts=generation_context)

        citations: list[GenerationCitation] = self.generation_service.build_citations(
            contexts=generation_context, answer=response
        )

        generated_result: GenerationResult = GenerationResult(
            answer=response, citations=citations
        )

        return generated_result
