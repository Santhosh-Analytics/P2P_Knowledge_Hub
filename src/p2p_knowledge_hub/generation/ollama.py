from p2p_knowledge_hub.core.timing import latency_decorator
from p2p_knowledge_hub.generation.base_generator import BaseGenerator
from p2p_knowledge_hub.models.generation_context import GenerationContext
from ollama import chat
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.core.logger import AppLogger

settngs = get_settings()
logger = AppLogger(settngs.logs).get_logger(__name__)


class OllamaGeneration(BaseGenerator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @latency_decorator
    def generate(self, query: str, contexts: list[GenerationContext]) -> str:

        formatted_context = self._format_context(contexts)
        prompt_template = (
            "Answer ONLY from the provided context.\n"
            "Rules:\n"
            "1. Do not use information that is not supported by the context.\n"
            "2. Cite each factual statement using [Source N].\n"
            "3. If the context contains information relevant to the question, use that information to answer even if the wording differs from the question.\n"
            "3. Add the citation immediately after the claim it supports.\n"
            "4. Never invent a source number. Use only source labels provided below.\n"
            "5. Only say I don't know when none of the provided sources contain information relevant to the question.\n"
            "6. Keep the answer concise."
            f"Context:\n{formatted_context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_template,
                },
            ],
            options={
                "num_predict": 450,
            },
            think=False,
        )

        logger.info(f"{contexts}")
        logger.info(f"Prompt eval count - {response['prompt_eval_count']}")
        logger.info(
            f"Prompt eval duration - {
                response['prompt_eval_duration'] / 1_000_000_000
            } secs"
        )
        logger.info(f"Eval count - {response['eval_count']}")
        logger.info(f"Eval duration - {response['eval_duration'] / 1_000_000_000} secs")
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
