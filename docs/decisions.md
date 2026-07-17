# ADR-001: Duplicate Document Handling

## Decision

The system identifies duplicate documents using a file hash.

If an identical document already exists, the ingestion service rejects the upload and returns metadata about the existing document.

## Reason

- Prevent duplicate embeddings
- Reduce storage
- Reduce indexing cost
- Avoid duplicate retrieval results

## Future Consideration

V2 will support explicit re-indexing for embedding upgrades, chunking changes, or document versioning.
