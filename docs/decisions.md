<!-- ADR = Architecture Decision Record. -->

<!-- P2P Knowledge Hub — Architecture Decision Records  -->

This document records the major architectural decisions made while building P2P Knowledge Hub. The goal is to preserve why a choice was made, its trade-offs, and what would cause the decision to change.

<!-- toc -->

- [ADR-001: Centralized application configuration](#adr-001-centralized-application-configuration)
    * [Decision](#decision)
    * [Reason](#reason)
    * [Future Consideration](#future-consideration)
- [ADR-002: Separate settings by concern](#adr-002-separate-settings-by-concern)
    * [Decision](#decision-1)
    * [Reason](#reason-1)
    * [Future Consideration](#future-consideration-1)
- [ADR-003: Duplicate Document Handling](#adr-003-duplicate-document-handling)
    * [Decision](#decision-2)
    * [Reason](#reason-2)
    * [Trade-offs](#trade-offs)
    * [Future Consideration](#future-consideration-2)
- [ADR-004: PostgreSQL + SQLAlchemy for document metadata](#adr-004-postgresql--sqlalchemy-for-document-metadata)
    * [Decision](#decision-3)
    * [Reason](#reason-3)
    * [Future Consideration](#future-consideration-3)
- [ADR-005: Format-specific document loaders](#adr-005-format-specific-document-loaders)
    * [Decision](#decision-4)
    * [Reason](#reason-4)
    * [Trade-offs](#trade-offs-1)
    * [Future Consideration](#future-consideration-4)
- [ADR-006 Chunk model carries retrieval/debug metadata](#adr-006-chunk-model-carries-retrievaldebug-metadata)
    * [Decision](#decision-5)
    * [Reason](#reason-5)
    * [Future Consideration](#future-consideration-5)
- [ADR-007 Dedicated in-memory BM25 lexical index](#adr-007-dedicated-in-memory-bm25-lexical-index)
    * [Decision](#decision-6)
    * [Reason](#reason-6)
    * [Trade-offs](#trade-offs-2)
    * [Future Consideration](#future-consideration-6)
- [ADR-008: ChromaDB persists chunk content; BM25 is reconstructed](#adr-008-chromadb-persists-chunk-content-bm25-is-reconstructed)
    * [Decision](#decision-7)
    * [Reason](#reason-7)
    * [Trade-offs](#trade-offs-3)
        + [Advantages](#advantages)
        + [Disadvantages](#disadvantages)
    * [Future Consideration](#future-consideration-7)
- [ADR-009: Hybrid retrieval followed by Cross-Encoder reranking](#adr-009-hybrid-retrieval-followed-by-cross-encoder-reranking)
    * [Decision](#decision-8)
    * [Reason](#reason-8)
    * [Trade-offs](#trade-offs-4)
    * [Future consideration](#future-consideration)
- [ADR-010: Deterministic citation resolution](#adr-010-deterministic-citation-resolution)
    * [Decision](#decision-9)
    * [Reason](#reason-9)
    * [Trade-offs](#trade-offs-5)
    * [Future consideration](#future-consideration-1)
- [ADR-011: FastAPI lifespan for shared RAG resources](#adr-011-fastapi-lifespan-for-shared-rag-resources)
    * [Decision](#decision-10)
    * [Reason](#reason-10)
    * [Future consideration](#future-consideration-2)
- [ADR-012: Measure latency at pipeline boundaries](#adr-012-measure-latency-at-pipeline-boundaries)
    * [Decision](#decision-11)
    * [Reason](#reason-11)
    * [Future consideration](#future-consideration-3)
- [ADR-013: Disable Qwen3 thinking for RAG answer synthesis](#adr-013-disable-qwen3-thinking-for-rag-answer-synthesis)
    * [Decision](#decision-12)
    * [Reason](#reason-12)
    * [Trade-offs](#trade-offs-6)
    * [Future consideration](#future-consideration-4)
    * [ADR-014: Keep V1 simple; optimize from measurements](#adr-014-keep-v1-simple-optimize-from-measurements)
    * [Decision](#decision-13)
    * [Reason](#reason-13)
    * [Future consideration](#future-consideration-5)

<!-- tocstop -->

# ADR-001: Centralized application configuration

Status: Accepted

## Decision

Use pydantic-settings with application settings composed under src/p2p_knowledge_hub/settings/. Runtime values are configurable through the project's settings sources rather than being hard-coded throughout services.

## Reason

- Centralizes configuration.
- Makes model names, logging, runtime paths, chunking, reranking, and generation settings replaceable.
- Makes testing and environment-specific configuration easier.
- Prevents individual modules from independently inventing configuration behavior.

## Future Consideration

Keep the hierarchy documented alongside the actual Settings source configuration and update this ADR if configuration precedence changes.

# ADR-002: Separate settings by concern

Status: Accepted

## Decision

Use a main settings object to compose settings for concerns such as logging, exceptions, runtime directories, chunking, embeddings, reranking, and generation.

## Reason

A single settings entry point gives the application a consistent configuration surface while smaller settings models keep unrelated configuration concerns separated.

## Future Consideration

No change is currently required. Split settings further only when a new subsystem has enough configuration to justify it.

# ADR-003: Duplicate Document Handling

Status: Accepted

## Decision

Identify duplicate documents using:

`source_system + business_process + file_hash`
The file hash is SHA-256 and is computed incrementally so large files do not need to be loaded into memory solely for hashing.

If the same document already exists for the same source system and business process, ingestion rejects the duplicate instead of producing another set of embeddings.

## Reason

- Prevent duplicate embeddings
- Reduce storage
- Reduce indexing cost
- Avoid duplicate retrieval results
- Preserve a clear relationship between an ingested source and its indexed representation.

## Trade-offs

The current key assumes one primary business process for a document. The same bytes may legitimately appear under another process/source combination.

## Future Consideration

V1 keeps this model simple. Explicit document versioning/re-indexing can later support embedding-model changes, chunking changes, and updated source documents.

# ADR-004: PostgreSQL + SQLAlchemy for document metadata

Status: Accepted

## Decision

Store document-level metadata in PostgreSQL and access it through SQLAlchemy. Domain/API data remains represented with Pydantic models rather than exposing ORM records through the application.

## Reason

- Document metadata needs durable relational persistence.
- Database constraints can protect invariants such as duplicate-document rules.
- Separating domain models from ORM records reduces persistence coupling.
- Synchronous access is simpler and sufficient until measurements show database I/O is a bottleneck.

## Future Consideration

Move to asynchronous database access only when workload measurements justify the added complexity.

# ADR-005: Format-specific document loaders

Status: Accepted

## Decision

Implement small format-specific loaders (currently PDF, DOCX, and Markdown as supported by the project) rather than adopting a large ingestion framework such as LangChain or Unstructured for V1.

## Reason

- Lower dependency overhead.
- Easier debugging.
- Direct control over extracted page/section metadata.
- Avoid premature framework complexity while learning and validating the ingestion pipeline.

## Trade-offs

Supporting many formats requires additional loader implementations and maintenance.

## Future Consideration

Add formats such as plain text, JSON, and HTML when required. Consider OCR for scanned documents. Revisit a document-processing framework only if format breadth or operational complexity makes it worthwhile.

# ADR-006 Chunk model carries retrieval/debug metadata

Status: Accepted

## Decision

Represent chunks explicitly with identifiers, ordering/version information where applicable, document linkage, text, page information, and optional structural metadata such as section/title.

Use document-wide chunk ordering rather than resetting the chunk index independently for every page/section.

## Reason

- Makes retrieval results traceable to their source.
- Supports citations.
- Helps inspect chunking failures and retrieval behavior.
- Allows future experiments with chunking strategies without losing source identity.
- Global ordering makes reconstructing neighboring chunks easier.

## Future Consideration

Expand chunk lifecycle/version metadata if document re-indexing becomes a first-class workflow.

# ADR-007 Dedicated in-memory BM25 lexical index

Status: Accepted

## Decision

Use an in-memory BM25 index built from active DocumentChunk text.

Chunkers produce retrieval-neutral chunks. BM25 tokenization and corpus statistics belong to a dedicated lexical-index component rather than the chunker.

## Reason

- Supports exact/lexical matching alongside semantic retrieval.
- Keeps chunk creation independent of retrieval algorithms.
- Avoids corpus preprocessing on every query.
- Provides a simple implementation suitable for the current corpus.

## Trade-offs

- The index is not inherently persistent.
- The corpus must fit in memory.
- Rebuilding becomes increasingly expensive as the corpus grows.

## Future Consideration

For a substantially larger corpus, evaluate a persistent sparse retrieval engine such as Elasticsearch/OpenSearch or another appropriate lexical index.

# ADR-008: ChromaDB persists chunk content; BM25 is reconstructed

## Decision

Do not create a separate PostgreSQL/local chunk store for the current MVP.

ChromaDB persists the chunk IDs, text, metadata, and embedding vectors. PostgreSQL persists document-level metadata.

BM25 remains in memory. At application startup:

ChromaDB
↓
fetch persisted chunks
↓
reconstruct DocumentChunk objects
↓
BM25Index.build(chunks)
↓
lexical retrieval available

After successful ingestion, V1 can rebuild BM25 from the persisted corpus.

BM25Index itself remains independent of ChromaDB and accepts list[DocumentChunk].

## Reason

The text needed to reconstruct BM25 already exists in ChromaDB. Introducing another chunk persistence layer in the MVP would create an additional source that must be synchronized during ingestion, deletion, updates, and version changes.

The current corpus is small enough that rebuilding BM25 is inexpensive.

## Trade-offs

### Advantages

- No duplicate chunk persistence.
- Fewer stores to synchronize.
- BM25 remains independent of ChromaDB.
- Lexical state can be reconstructed after restart.
- Simple MVP architecture.

### Disadvantages

- ChromaDB temporarily acts as the persisted source for chunk content.
- Startup depends on successful chunk reconstruction.
- Full BM25 rebuild cost grows with corpus size.
- ChromaDB is doing more than acting purely as a derived vector index.

## Future Consideration

At larger scale, introduce a canonical document_chunks store:

       canonical chunk store
               |
         DocumentChunk
          /         \
         v           v
     ChromaDB       BM25

vector index lexical index

Both retrieval indexes could then be treated as disposable derived indexes.

V2 should evaluate incremental BM25 updates only when corpus size or measured rebuild latency justifies them.

# ADR-009: Hybrid retrieval followed by Cross-Encoder reranking

Status: Accepted

## Decision

Use both BM25 lexical retrieval and SentenceTransformer dense retrieval to produce candidates, combine them through the hybrid retriever, and rerank the candidate set with a Cross-Encoder before generation.

## Reason

BM25 and dense retrieval solve different failure modes. Lexical retrieval is useful for exact terminology, identifiers, and domain phrases; dense retrieval improves semantic matching. A Cross-Encoder can then score query/chunk pairs more precisely than the initial bi-encoder retrieval stage.

Separating candidate retrieval (candidate_k) from final context size (top_k) allows recall and generation-context size to be tuned independently.

## Trade-offs

Cross-Encoder reranking adds latency, but local profiling currently shows generation—not reranking—is the dominant latency cost.

## Future consideration

Tune candidate and final k values using an evaluation dataset rather than intuition alone.

# ADR-010: Deterministic citation resolution

Status: Accepted

## Decision

Provide numbered contexts to the generator ([Source 1], [Source 2], ...). The LLM may reference these source numbers in its answer, but Python code parses the references and constructs the final citation objects.

The model does not generate authoritative chunk IDs, paths, page metadata, or other citation metadata.

## Reason

The application already knows the source-to-chunk mapping.

Avoids asking the LLM to reproduce structured identifiers it can get wrong.

Citation metadata remains deterministic and auditable.

Makes citation behavior independently testable.

## Trade-offs

The generator must reliably emit the agreed [Source N] syntax. Invalid/out-of-range source references need to be ignored or handled explicitly.

## Future consideration

Add citation validation metrics and tests, including unsupported claims and invalid source references.

# ADR-011: FastAPI lifespan for shared RAG resources

Status: Accepted

## Decision

Create expensive/shared application resources during FastAPI lifespan startup and expose pipeline services through dependency injection.

Shared resources include the embedding service and vector store used by both ingestion and retrieval. The RAG pipeline and document pipeline receive their dependencies rather than independently constructing duplicate model/store instances.

## Reason

Avoid loading embedding models multiple times.

Avoid unnecessary Chroma clients/resources.

Reduces per-request construction cost.

Makes ownership of long-lived resources explicit.

Improves testability through dependency injection.

## Future consideration

Add explicit shutdown/cleanup only for resources that require it. Revisit process-level model sharing when deploying with multiple workers.

# ADR-012: Measure latency at pipeline boundaries

Status: Accepted

## Decision

Use a reusable decorator based on time.perf_counter() to log execution latency for important pipeline methods while preserving the wrapped function's return value and metadata.

Measure retrieval, reranking, database lookup, context construction, generation, and total RAG latency separately.

## Reason

End-to-end latency alone cannot identify the failing/slow stage. Stage-level timing showed that local Cross-Encoder retrieval was measured in hundreds of milliseconds while generation could take tens of seconds.

This allowed optimization to target the actual bottleneck instead of prematurely changing retrieval infrastructure.

## Future consideration

Move from plain latency log lines to structured metrics/tracing if the application is deployed.

# ADR-013: Disable Qwen3 thinking for RAG answer synthesis

Status: Accepted for current local generator

## Decision

Run the current Qwen3 Ollama generator with thinking disabled for normal RAG answer synthesis and bound the maximum generated output.

The prompt explicitly requires answers to use provided context, accept semantically relevant wording rather than exact query wording, cite factual claims using [Source N], and return an unknown answer only when the supplied contexts do not contain relevant information.

## Reason

Local profiling showed that thinking consumed a large generation budget for straightforward grounded synthesis. In measured experiments, disabling thinking reduced generation from tens of seconds to low single-digit generation time for a representative query.

A prompt adjustment was required after disabling thinking because the smaller model initially became overly conservative and returned an unsupported “don't know” despite relevant retrieved context.

## Trade-offs

Disabling thinking may reduce quality on questions requiring more complex multi-step reasoning. Current observations come from a small local corpus and are not production benchmarks.

## Future consideration

Evaluate generator configuration against a representative question set. Route genuinely complex questions differently only if evaluation demonstrates a quality benefit.

## ADR-014: Keep V1 simple; optimize from measurements

Status: Accepted

## Decision

Prefer the simplest architecture that satisfies the current portfolio/MVP requirements. Defer incremental BM25 indexing, a canonical chunk database, asynchronous database access, large ingestion frameworks, and other scale-oriented changes until measurements or requirements justify them.

## Reason

The project is intended to demonstrate an understandable, production-oriented RAG architecture rather than accumulate infrastructure that the current corpus does not need.

## Future consideration

Use evaluation quality, corpus size, latency, concurrency, and operational requirements as triggers for architectural changes rather than adding components preemptively.
