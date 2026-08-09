# Day 9 — Hybrid Search + Reciprocal Rank Fusion (RRF)

**Vault path:** `/home/san/Obsidian/Python/NLP_DSA/weeks/`
**Date:** 2026-06-17
**Status:** ✅ Complete

---

## 1. Why Hybrid Search?

Neither BM25 nor dense retrieval is complete alone:

| System | Strength | Weakness |
|---|---|---|
| BM25 | Exact keyword match — great for codes, IDs, terminology | Misses semantic meaning — "stuck invoice" finds nothing |
| Dense | Semantic meaning — understands intent and paraphrase | Misses exact terms — "PO 4521" may not surface correctly |

> **Mental model:** BM25 is a keyword expert. Dense retrieval is a meaning expert. Hybrid search combines both signals.

**P2P example:**
- `"PO 4521 three-way match failed"` → BM25 wins (exact ID match)
- `"why is my invoice stuck"` → Dense wins (semantic intent)

---

## 2. The Core Problem with Combining Scores

BM25 scores live in a different universe than dense scores:
- BM25 might return `127.4` for rank 1
- Dense might return `0.87` for rank 1

You **cannot add these directly** — the scales are incomparable.

**Solution:** Throw away the scores. Use only **rank position** — that's comparable across any system.

---

## 3. Reciprocal Rank Fusion (RRF)

### Formula
For each document in each ranked list:

```
RRF_score = 1 / (k + rank)
```

Then **sum** RRF scores across all systems per document.

### The k parameter (smoothing constant)
- Default: `k = 60`
- **Purpose:** Controls how steeply rank 1 dominates over lower ranks

```
k=0  → Rank 1: 1.0,  Rank 2: 0.5   → huge gap, rank 1 dominates
k=60 → Rank 1: 0.0164, Rank 2: 0.0161 → gentle slope, lower ranks still count
```

> **Analogy:** k=60 is like saying "even rank 10 deserves a fair hearing" — useful when your top-ranked result might be a false positive.

### Why RRF rewards consensus
A document at **rank 1 in BM25 AND rank 1 in dense** gets:
`1/(60+1) + 1/(60+1) = 0.0328`

A document at **rank 1 in BM25 BUT rank 47 in dense** gets:
`1/(60+1) + 1/(60+47) = 0.0164 + 0.0093 = 0.0257`

Two independent signals agreeing = higher confidence = higher final rank.

---

## 4. Full Pipeline

```
Query
  │
  ├──► BM25 retrieval ──► ranked list (doc_idx, rank)
  │                                         │
  │                                         ▼
  └──► Dense retrieval ──► ranked list ──► RRF fusion ──► Final ranked list
                           (doc_idx, rank)
```

---

## 5. Code — Full Hybrid Search from Scratch

```python
import string
import numpy as np
from sentence_transformers import SentenceTransformer

docs = [
    "Invoice INV-1001 is pending three-way match approval",
    "PO 4521 has been approved by the procurement team",
    "Vendor payment for INV-1001 is overdue by 30 days",
    "Goods receipt for PO 4521 has not been recorded",
    "Three-way match requires PO, GRN and invoice to align",
]
query = "INV-1001 three way match"

# --- Text Cleaning ---
def clean_text(text):
    if isinstance(text, list):
        cleaned = []
        for sent in text:
            sent = sent.lower()
            sent = "".join(ch for ch in sent if ch not in string.punctuation)
            cleaned.append(sent.strip())
        return cleaned
    elif isinstance(text, str):
        text = text.lower()
        text = "".join(ch for ch in text if ch not in string.punctuation)
        return text.strip()

# --- BM25 helpers ---
def compute_tf(text):
    tfs = []
    for sent in text:
        tf = {}
        for word in sent.split():
            tf[word] = tf.get(word, 0) + 1
        tfs.append(tf)
    return tfs

def compute_idf(cleaned_text):
    unique_words = {}
    doc_len = len(cleaned_text)
    for sent in cleaned_text:
        for word in set(sent.split()):
            unique_words[word] = unique_words.get(word, 0) + 1
    return {word: np.log(doc_len / count) for word, count in unique_words.items()}

# --- BM25 ---
def compute_bm25(query, text, k=1.5, b=0.75):
    cleaned_text = clean_text(text)
    tfs = compute_tf(cleaned_text)
    idf = compute_idf(cleaned_text)
    avg_doc_len = sum(len(sent.split()) for sent in cleaned_text) / len(cleaned_text)
    query = clean_text(query)
    scores = []
    for i, sent in enumerate(cleaned_text):
        doc_len = len(sent.split())
        score = 0
        for word in query.split():
            tf_q = tfs[i].get(word, 0)
            idf_score = idf.get(word, 0)
            score += (
                idf_score
                * (tf_q * (k + 1))
                / (tf_q + k * (1 - b + b * (doc_len / avg_doc_len)))
            )
        scores.append(score)
    return scores

# --- Dense Retrieval ---
def compute_dense_scores(query, docs):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    doc_embeddings = model.encode(clean_text(docs))
    query_embedding = model.encode(clean_text(query))
    scores = []
    for doc_emb in doc_embeddings:
        score = float(model.similarity(query_embedding, doc_emb))
        scores.append(score)
    return scores

# --- RRF Fusion ---
def reciprocal_rank_fusion(bm25_scores, dense_scores, docs, k=60):
    # Convert scores to ranked dicts — sort descending, assign rank by position
    def to_ranked(scores):
        scored = {i: s for i, s in enumerate(scores)}
        sorted_scores = dict(sorted(scored.items(), key=lambda x: x[1], reverse=True))
        ranked = {}
        for rank, (doc_idx, _) in enumerate(sorted_scores.items(), start=1):
            ranked[doc_idx] = (rank, 1 / (k + rank))
        return ranked

    sparse_ranked = to_ranked(bm25_scores)
    dense_ranked = to_ranked(dense_scores)

    # Combine RRF scores per doc
    final_rrf = []
    for doc_idx in range(len(docs)):
        rrf_score = sparse_ranked[doc_idx][1] + dense_ranked[doc_idx][1]
        final_rrf.append((doc_idx, rrf_score))

    # Sort final list descending
    final_rrf = sorted(final_rrf, key=lambda x: x[1], reverse=True)
    return final_rrf

# --- Run ---
bm25_scores = compute_bm25(query, docs)
dense_scores = compute_dense_scores(query, docs)
results = reciprocal_rank_fusion(bm25_scores, dense_scores, docs)

print("\n--- Hybrid Search Results ---")
for final_rank, (doc_idx, rrf_score) in enumerate(results, start=1):
    print(f"Rank {final_rank} | Doc {doc_idx} | RRF: {rrf_score:.4f} | {docs[doc_idx]}")
```

---

## 6. Key Bugs Fixed During Build

| Bug | Cause | Fix |
|---|---|---|
| All BM25 scores zero | Iterating over string characters instead of words | `query.split()` |
| Doc 2 scoring zero despite having INV-1001 | TF computed on uncleaned docs but query was cleaned | Clean both docs and query before BM25 |
| RRF scores all equal/sequential | Forgot to sort scores before assigning ranks | `sorted(..., reverse=True)` before rank assignment |
| Fragile RRF loop | `zip()` on dict keys assumes same order | Loop over `range(len(docs))` and look up both dicts |

---

## 7. Interview-Ready Summary

**Q: What is hybrid search?**
Combining sparse retrieval (BM25) and dense retrieval (embeddings) to get the benefits of both — exact keyword matching and semantic understanding.

**Q: Why not just normalize BM25 and dense scores and add them?**
Score scales are incomparable. BM25 is unbounded; cosine similarity is 0–1. Normalization is fragile because gaps between scores within one system may be meaningless.

**Q: What is RRF and why does it work?**
Reciprocal Rank Fusion uses only rank position, not raw scores. `1/(k+rank)` converts rank to a comparable value. Summing across systems rewards documents that both retrievers agree are relevant.

**Q: What does the k parameter do in RRF?**
It's a smoothing constant (default 60). Higher k = gentler slope = lower-ranked documents still get meaningful scores. Prevents rank 1 from dominating everything.

---

## 8. Connections to Your Projects

- **p2p-rag-assistant** → Add hybrid search as the retrieval layer; BM25 handles PO numbers and invoice IDs, dense handles intent-based queries
- **EnterpriseKnowledgeAssistant** → Same pattern; enterprise docs have both terminology and semantic content

---

*Day 9 complete ✅*
