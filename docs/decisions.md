<!-- ADR = Architecture Decision Record. -->

<!-- toc -->

- [ADR-001: Pydantic Settings](#adr-001-pydantic-settings)
    * [Decision](#decision)
    * [Reason](#reason)
    * [Future Consideration](#future-consideration)
- [ADR-002: App Settings](#adr-002-app-settings)
    * [Decision](#decision-1)
    * [Reason](#reason-1)
    * [Future Consideration](#future-consideration-1)
- [ADR-003: Duplicate Document Handling](#adr-003-duplicate-document-handling)
    * [Decision](#decision-2)
    * [Reason](#reason-2)
    * [Future Consideration](#future-consideration-2)
- [ADR-004: ORM Layer](#adr-004-orm-layer)
    * [Decision](#decision-3)
    * [Reason](#reason-3)
    * [Future Consideration](#future-consideration-3)
- [ADR-005: Document Loader](#adr-005-document-loader)
    * [Decision](#decision-4)
    * [Reason](#reason-4)
    * [Future Consideration](#future-consideration-4)
- [ADR-006 Chunking](#adr-006-chunking)
    * [Decision](#decision-5)
    * [Reason](#reason-5)
    * [Future Consideration](#future-consideration-5)
- [For uniquely identifying and ordering all chunks in one document, I recommend a global index across the document.](#for-uniquely-identifying-and-ordering-all-chunks-in-one-document-i-recommend-a-global-index-across-the-document)
- [ADR-007 Lexical Indexing Strategy](#adr-007-lexical-indexing-strategy)
    * [Decision](#decision-6)
    * [Reason](#reason-6)
        + [Cons](#cons)
    * [Future Consideration](#future-consideration-6)
    * [ADR-008: Chunk Persistence and BM25 Index Reconstruction](#adr-008-chunk-persistence-and-bm25-index-reconstruction)
        + [Decision](#decision-7)
        + [Reason](#reason-7)
        + [Trade-offs](#trade-offs)
        + [Future Consideration](#future-consideration-7)

<!-- tocstop -->

# ADR-001: Pydantic Settings

## Decision

The Pydantic settings uses config.toml in the root directory to override default
settings. The Pydantic respects the settings in the following order. If
any conflict config.toml will take precedence unless we use env prefix.

Env Prefix -> Config.toml -> init settings -> -> dot env -> Secrets

## Reason

The hierarchy is maintained to avoid unnecessary influence by duplicate settings.

## Future Consideration

Currently no plan to change anything.

# ADR-002: App Settings

## Decision

Created main settings at the /src/p2p_knowledge_hub/settings/main.py that
wires all settings inside the folder. All other settings implemented in the
same settings folder. Each module (logger, exception, Runtime directory creation,Ingestion) handles own function settings.

## Reason

It helps implementing the settings safer and appropriate way. If we need to
change any options for testing or replace any other options we can use
config.toml rather roaming over the modules.

## Future Consideration

Currently no plan to change anything.

# ADR-003: Duplicate Document Handling

## Decision

The system identifies duplicate documents using a source_system + business_process + file_hash. It uses incremental SHA-256 hashing so we can also read large files and the hashing mechanism handles hashing incrementally.

If an identical document already exists, the ingestion service rejects the upload and returns metadata about the existing document.

## Reason

- Prevent duplicate embeddings
- Reduce storage
- Reduce indexing cost
- Avoid duplicate retrieval results

## Future Consideration

V1 assumes one primary business process per document. Multi-process document mapping may be added later.
V2 will support explicit re-indexing for embedding upgrades, chunking changes, or document versioning.

# ADR-004: ORM Layer

## Decision

I used Pydantic Database (db) (SQL Alchemy) to define the schema of the
database. In this project i use this database to store the file metadata
and file hash. So we can use it to avoid duplication.

## Reason

## Future Consideration

Currently the db access will be synchronous. Later, FastAPI can move to async only if measurements show a need.

# ADR-005: Document Loader

## Decision

Keep the loader simple and format-specific (PDF, DOCX, Markdown) in v1, without adopting large frameworks like LangChain or Unstructured.

## Reason

- Reduces dependency overhead for a beginner-friendly implementation.
- Easier debugging and control over parsing logic.
- Avoids premature complexity before validating ingestion pipeline.

Since i am beginner i would like to start with small. Once it is
successful, i may add few other document types.

## Future Consideration

- Add support for Plain Text, JSON, HTML.
- Extend to OCR-based ingestion for scanned images.
- Revisit framework adoption if scaling demands modularity or multi-format support.

# ADR-006 Chunking

## Decision

Keeping core metadata such as chunk id, chunk index, chunk version, chunk
status, created at, document id, text, page no, and section optionally. This
will help to keep audit trail and debug friendly.

## Reason

- Keep versioning helps in rollback if any issues.
- Experiment with different chunk size and overlap without noise.

## Future Consideration

None

# For uniquely identifying and ordering all chunks in one document, I recommend a global index across the document.

# ADR-007 Lexical Indexing Strategy

Pre-compute corpus statistics

Use an in-memory BM25 lexical index built from active document chunks.

## Decision

Chunkers produce source-neutral DocumentChunk objects. BM25 tokenization and corpus statistics are handled by a dedicated lexical-index component to avoid coupling chunk generation to one retrieval strategy.

## Reason

- Fast lexical retrieval
- Separate lexical indexing from chunk generation
- No preprocessing during queries
- Exact keyword matching
- Simple implementation for V1

### Cons

- Index rebuilt on application restart
- Entire corpus must fit in memory
- Not suitable for millions of chunks

## Future Consideration

Replace the in-memory BM25 index with Elasticsearch/OpenSearch or another persistent sparse retrieval engine if the corpus grows significantly.

## ADR-008: Chunk Persistence and BM25 Index Reconstruction

### Decision

For the current MVP, `DocumentChunk` objects will not be persisted in a
separate local chunk store or PostgreSQL table.

ChromaDB will persist:

- chunk IDs
- chunk text
- chunk metadata
- embedding vectors

PostgreSQL will continue to persist document-level metadata.

The BM25 index is an in-memory index and will be rebuilt when the application
starts.

The startup flow will be:

ChromaDB
→ fetch persisted chunk text and metadata
→ reconstruct `DocumentChunk` objects
→ `BM25Index.build(chunks)`
→ BM25 index available for lexical retrieval

When new documents are indexed, the BM25 corpus can be rebuilt from the
current persisted chunks.

### Reason

`rank_bm25.BM25Okapi` is currently used as an in-memory lexical index.
Unlike the ChromaDB vector index, the BM25 index does not automatically
persist between application restarts.

The chunk text required to rebuild BM25 is already stored in the persistent
ChromaDB collection.

Creating an additional local chunk store would introduce another persistence
layer:

PostgreSQL

- ChromaDB
- local chunk storage

This would increase synchronization complexity, particularly during document
updates, version changes, and deletion.

The current project has a small corpus, so rebuilding BM25 from persisted
chunks is inexpensive and keeps the MVP architecture simple.

`BM25Index` should remain independent of ChromaDB. It should only accept:

`list[DocumentChunk]`

A separate service/infrastructure component is responsible for retrieving
persisted chunks and providing them to `BM25Index`.

### Trade-offs

Advantages:

- avoids duplicate chunk persistence
- keeps BM25 implementation independent of ChromaDB
- BM25 can be rebuilt after application restart
- simpler MVP architecture
- fewer stores to synchronize
- existing ChromaDB data can be reused

Disadvantages:

- ChromaDB temporarily acts as the persistent source for chunk content
- startup requires rebuilding the BM25 index
- rebuilding may become expensive with a large corpus
- lexical retrieval availability depends on successful chunk reconstruction

### Future Consideration

For a larger production deployment, persist chunks in a dedicated
`document_chunks` table or another canonical document/chunk store.

The architecture could then become:

PostgreSQL / canonical chunk store
↓
DocumentChunk
/ \
↓ ↓
ChromaDB BM25
vector lexical
index index

In that architecture, ChromaDB and BM25 are derived indexes rather than the
source of truth.

This would allow either retrieval index to be deleted and rebuilt from the
canonical chunk data.

For the current portfolio MVP, this additional persistence layer is deferred
until scale or operational requirements justify it.
