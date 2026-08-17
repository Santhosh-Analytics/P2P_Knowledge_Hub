from p2p_knowledge_hub.core.timing import latency_decorator
from p2p_knowledge_hub.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork
from uuid import UUID
from p2p_knowledge_hub.models.retrieved_chunk import RetrievedChunk
from p2p_knowledge_hub.models.generation_citation import GenerationCitation
from p2p_knowledge_hub.models.document import Document
from p2p_knowledge_hub.models.generation_context import GenerationContext
from p2p_knowledge_hub.models.db.sessions import SessionManager
from sqlalchemy.exc import IntegrityError, OperationalError
from p2p_knowledge_hub.exceptions.sqlalchemy_error import DBConnectionError
from p2p_knowledge_hub.exceptions.generation_error import DocumentIDNotFoundError
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
import re

settings = get_settings()
_logger = AppLogger(settings.logs).get_logger(__name__)


class GenerationService:
    def unique_documents(self, reranked_documents: list[RetrievedChunk]) -> set[UUID]:

        return {
            retrieved_chunk.chunk.document_id for retrieved_chunk in reranked_documents
        }

    @latency_decorator
    def get_document_record(self, ids: set[UUID]) -> dict[UUID, Document]:

        with SQLAlchemyUnitOfWork(SessionManager().session_factory) as uow:
            try:
                document_dict: dict[UUID, Document] = uow.document.get_by_ids(ids)
            except OperationalError as e:
                error_message = str(e.__dict__.get("orig", e))
                _logger.error(
                    f"[bold red blink] Failed to retrieve citation metadata.{ids}. \n\n{error_message}",
                    extra={"markup": True},
                )
                if "connection failed: connection to server" in error_message:
                    raise DBConnectionError(
                        f"ERROR: Could not connect to the database.\n\n{error_message}"
                    )

            except IntegrityError as e:
                error_message = str(e.__dict__.get("orig", e))
                _logger.error(
                    f"[bold red blink]Failed to retrieve citation metadata.  '{ids}. \n\n{error_message}'",
                    extra={"markup": True},
                )
                raise

            except Exception as e:
                _logger.error(
                    f"[bold red blink]Failed to retrieve citation metadata. '{ids}. \n\n{e}'",
                    extra={"markup": True},
                )
                raise
        return document_dict

    @latency_decorator
    def build_context(
        self,
        reranked_chunks: list[RetrievedChunk],
        documents: dict[UUID, Document],
    ) -> list[GenerationContext]:
        generated_context: list[GenerationContext] = []

        for reranked_chunk in reranked_chunks:
            document_id = reranked_chunk.chunk.document_id

            try:
                document = documents[document_id]
            except KeyError as exc:
                _logger.error(
                    f"Failed to retrieve citation metadata for document_id={document_id}"
                )
                raise DocumentIDNotFoundError(
                    f"Document metadata not found for document_id={document_id}"
                ) from exc

            generated_context.append(
                GenerationContext(
                    chunk_id=reranked_chunk.chunk.chunk_id,
                    text=reranked_chunk.chunk.text,
                    document_name=document.document_name,
                    page_no=reranked_chunk.chunk.page_no,
                    section=reranked_chunk.chunk.section,
                    title=reranked_chunk.chunk.title,
                    source_uri=document.source_uri,
                )
            )

        return generated_context

    def build_citations(
        self, answer: str, contexts: list[GenerationContext]
    ) -> list[GenerationCitation]:
        source_ids: list[str] = re.findall(r"\[Source (\d+)\]", answer)
        unique_source_ids: list[int] = list(dict.fromkeys(map(int, source_ids)))

        citations: list[GenerationCitation] = []

        for i in unique_source_ids:
            if 1 <= i <= len(contexts):
                context = contexts[i - 1]
                citations.append(
                    GenerationCitation(
                        source_id=i,
                        chunk_id=context.chunk_id,
                        document_name=context.document_name,
                        page_no=context.page_no,
                        section=context.section,
                        title=context.title,
                        source_uri=context.source_uri,
                    )
                )
        return citations
