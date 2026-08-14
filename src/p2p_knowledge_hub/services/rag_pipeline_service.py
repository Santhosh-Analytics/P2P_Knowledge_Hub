from p2p_knowledge_hub.generation.base_generator import BaseGenerator
from p2p_knowledge_hub.generation.generation_service import GenerationService
from p2p_knowledge_hub.services.retrieval_pipeline_service import (
    RetrievalPipelineService,
)


class RAGPipelineService:
    def __init__(
        self,
        retrieval_service: RetrievalPipelineService,
        generation_service: GenerationService,
        generator: BaseGenerator,
    ) -> None:
    
    def answer
