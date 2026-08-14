from p2p_knowledge_hub.generation.base_generator import BaseGenerator
from p2p_knowledge_hub.models.generation_context import GenerationContext
from ollama import chat


class OllamaGeneration(BaseGenerator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, query: str, contexts: list[GenerationContext]) -> str:

        formatted_context = self._format_context(contexts)
        prompt_template = (
            f"Use the following pieces of context to answer the question.\n\n"
            f"{formatted_context}\n\n"
            f"Question: {query}\n"
            f"If you don't know the answer, just say you don't know."
        )

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_template,
                }
            ],
        )

        return response["message"]["content"]

    def _format_context(self, contexts: list[GenerationContext]) -> str:
        formatted: list[str] = []

        for index, context in enumerate(contexts, start=1):
            page = f"Page: {context.page_no}" if context.page_no is not None else ""

            section = f"Section: {context.section}" if context.section else ""

            title = f"Title: {context.title}" if context.title else ""

            source = f"Source: {context.source_uri}" if context.source_uri else ""

            metadata = " | ".join(
                item
                for item in (
                    context.document_name,
                    page,
                    section,
                    title,
                    source,
                )
                if item
            )

            formatted.append(f"[Source {index}]\n{metadata}\nContent:\n{context.text}")

        return "\n\n".join(formatted)
