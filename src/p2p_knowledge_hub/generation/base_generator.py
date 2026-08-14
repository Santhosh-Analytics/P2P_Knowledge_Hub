from abc import ABC, abstractmethod

from p2p_knowledge_hub.models.generation_context import GenerationContext


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, query: str, contexts: list[GenerationContext]) -> str:
        raise NotImplementedError
