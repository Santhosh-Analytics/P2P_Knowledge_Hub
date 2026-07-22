

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
- [ADR-004: Pydantic Database](#adr-004-pydantic-database)
    * [Decision](#decision-3)
    * [Reason](#reason-3)
    * [Future Consideration](#future-consideration-3)

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

# ADR-004: Pydantic Database

## Decision

I used Pydantic Database (db) (SQL Alchemy) to define the schema of the
database. In this project i use this database to store the file metadata
and file hash. So we can use it to avoid duplication.

## Reason

SQL Alchemy is a Object-Relational Mapper, meaning it maps python classes
to db tables and handles db operations.

## Future Consideration

Currently the db access will be synchronous. Later, FastAPI can move to async only if measurements show a need.
