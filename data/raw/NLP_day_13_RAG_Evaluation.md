---
id: NLP_day_13_RAG_Evaluation
aliases: []
tags: []
---

# Day 13 — RAG Evaluation (Interview Revision Notes)

## Goal

**Question interviewers are asking:**

> _"How do you know your RAG system is actually working?"_

Production systems should never be evaluated by:

- "The answer looks good."

Instead, use measurable evaluation metrics.

---

# 1. Evaluation Layers

## Retrieval Evaluation

Evaluates whether the retriever found good evidence.

Metrics:

- Context Precision
- Context Recall
- Recall@K
- Precision@K
- MRR
- NDCG

---

## Generation Evaluation

Evaluates whether the LLM used the evidence correctly.

Metrics:

- Faithfulness
- Answer Relevancy
- Hallucination Detection

---

# 2. Context Precision

### Definition

Measures **how much of the retrieved context is actually relevant** to answer the user's question.

In simple words:

> "Did we retrieve mostly useful chunks instead of noise?"

---

### High Context Precision

Retrieved:

- Chunk A ✅
- Chunk B ✅

Only relevant chunks.

---

### Low Context Precision

Retrieved:

- Chunk A ✅
- Chunk B ❌
- Chunk C ❌
- Chunk D ❌

Retriever sent unnecessary context.

---

### Why it matters

Low Context Precision causes:

- More token usage
- Higher cost
- Higher latency
- More noise
- Lost in the Middle

---

### Interview Definition

> Context Precision measures the proportion of retrieved context that is actually useful for answering the user's question.

---

# 3. Context Recall

### Definition

Measures whether the retrieved context contains **enough information** to answer the question completely.

---

### High Context Recall

Retriever returns one chunk.

That chunk contains everything needed.

✅ High Context Recall

---

### Low Context Recall

Retriever misses one important policy section.

LLM cannot answer completely.

❌ Low Context Recall

---

### Interview Definition

> Context Recall measures whether the retrieved context contains sufficient information for the LLM to generate a complete answer.

---

# Context Precision vs Context Recall

| Context Precision                     | Context Recall                      |
| ------------------------------------- | ----------------------------------- |
| Are retrieved chunks mostly relevant? | Did we retrieve enough information? |
| Focuses on noise                      | Focuses on completeness             |

---

# 4. Faithfulness

### Definition

Measures whether the generated answer is completely supported by the retrieved context.

---

### Example

Context:

```
Vendor onboarding requires:

- GST
- PAN
- Bank Details
```

LLM Answer:

```
GST
PAN
Bank Details
```

✅ High Faithfulness

---

LLM Answer:

```
GST
PAN
Bank Details
Police Verification
```

❌ Hallucination

❌ Low Faithfulness

---

### Important Interview Point

Faithfulness **does NOT measure truth**.

It measures:

> "Did the model stay grounded in the retrieved context?"

---

### Example

Knowledge base contains outdated information.

LLM summarizes it perfectly.

Faithfulness:

✅ High

Answer may still be factually outdated.

---

### Interview Definition

> Faithfulness measures whether every statement in the generated answer is supported by the retrieved context.

---

# 5. Answer Relevancy

### Definition

Measures whether the generated answer actually answers the user's question.

---

Example

Question:

```
What documents are required for Vendor Onboarding?
```

LLM Answer:

```
Vendor onboarding is the process of registering suppliers...
```

Factually correct.

Grounded.

But doesn't answer the question.

Answer Relevancy:

❌ Low

---

### Interview Definition

> Answer Relevancy measures how well the generated answer addresses the user's actual question.

---

# Faithfulness vs Answer Relevancy

| Faithfulness                        | Answer Relevancy            |
| ----------------------------------- | --------------------------- |
| Is the answer supported by context? | Did it answer the question? |

Possible combinations:

### High Faithfulness + High Relevancy

Ideal.

---

### High Faithfulness + Low Relevancy

Grounded answer.

Wrong intent.

---

### Low Faithfulness + High Relevancy

Answers the question.

Hallucinates facts.

---

# 6. Hallucination

### Definition

The LLM generates information **not supported by the retrieved context.**

Example:

Context:

```
Approval by Manager
```

LLM:

```
Approval by Director
```

Director never existed.

Hallucination.

---

# 7. Offline Evaluation

Purpose:

> "Should we deploy this model?"

Examples:

- Context Precision
- Context Recall
- Faithfulness
- Answer Relevancy
- Recall@K
- MRR
- NDCG

Advantages:

- Repeatable
- Cheap
- Fast
- Good for experiment comparison
- MLflow tracking

---

# 8. Online Evaluation

Purpose:

> "Is the deployed system helping real users?"

Monitor:

- User feedback
- 👍 / 👎
- User satisfaction
- Latency
- Cost
- Error rate
- Follow-up questions
- Time to resolution

Real users expose edge cases not present in benchmark datasets.

---

# Offline vs Online

| Offline             | Online               |
| ------------------- | -------------------- |
| Before deployment   | After deployment     |
| Controlled dataset  | Real users           |
| Compare experiments | Monitor production   |
| Prevent regressions | Detect real failures |

---

# 9. Automated Evaluation Pipeline

Manual evaluation does not scale.

Instead:

```
Question
     ↓
Retriever
     ↓
LLM
     ↓
Evaluation Pipeline
     ↓
Metrics
     ↓
Dashboard
```

Benefits:

- Detect regressions
- Compare experiments
- Continuous monitoring
- Faster debugging

Human review is still required for validation.

---

# 10. RAGAS (Conceptual)

Purpose:

Automatically evaluate RAG systems.

Metrics include:

- Context Precision
- Context Recall
- Faithfulness
- Answer Relevancy

Benefits:

- Saves manual effort
- Large-scale evaluation
- Experiment comparison

Limitation:

RAGAS is **an evaluator**, not ground truth.

Always validate important changes with human review.

---

# 11. Production Debugging Workflow

When users say:

> "The answer is wrong."

Follow this order:

```
1. Query
        ↓
2. Query Processing
        ↓
3. Retriever
        ↓
4. Reranker
        ↓
5. Prompt
        ↓
6. LLM
        ↓
7. Evaluation Metrics
```

Never blame the LLM first.

---

# Logs to Inspect

## Query

- User query
- Original query

---

## Query Processing

- Rewritten query
- Expanded query
- Intent preserved?

---

## Retriever

- Retrieved chunks
- Chunk IDs
- Metadata
- BM25 scores
- Dense scores
- Hybrid scores

---

## Reranker

- Before reranking
- After reranking

---

## Prompt

- Final prompt
- Context ordering
- Prompt truncation
- Number of chunks
- Lost in the Middle

---

## LLM

- Final answer
- Citations
- Token usage
- Latency

---

## Evaluation

- Context Precision
- Context Recall
- Faithfulness
- Answer Relevancy

---

# 12. Production Mindset

Always:

1. Isolate the failing stage.
2. Inspect logs and evidence.
3. Measure with metrics.
4. Fix the root cause.
5. Validate before deployment.
6. Monitor after deployment.

---

# Interview One-Liners

### Context Precision

> Measures how much of the retrieved context is actually relevant.

---

### Context Recall

> Measures whether the retrieved context contains enough information to answer the question completely.

---

### Faithfulness

> Measures whether the generated answer is fully supported by the retrieved context.

---

### Answer Relevancy

> Measures whether the generated answer actually addresses the user's question.

---

### Hallucination

> The model generates information not supported by the retrieved context.

---

### Offline Evaluation

> Used before deployment to compare experiments and prevent regressions.

---

### Online Evaluation

> Used after deployment to monitor real-user experience and production failures.

---

### RAGAS

> A framework that automates RAG evaluation using metrics like Context Precision, Context Recall, Faithfulness, and Answer Relevancy. It accelerates evaluation but should complement, not replace, human review.

---

# Interview Cheat Sheet

```
User Query
      ↓
Query Processing
      ↓
Retriever
      ↓
Context Precision
Context Recall
      ↓
Reranker
      ↓
Prompt
      ↓
LLM
      ↓
Faithfulness
Answer Relevancy
      ↓
Offline Evaluation
      ↓
Production Deployment
      ↓
Online Monitoring
      ↓
Human Review
```
