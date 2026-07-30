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
