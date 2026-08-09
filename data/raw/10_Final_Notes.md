---
id: 10_Final_Notes
aliases: []
tags: []
---
# Final Notes

<!-- toc -->

- [Transformer Full Architecture](#transformer-full-architecture)
    * [Encoder](#encoder)
        + [***Input Layer***](#input-layer)
        + [***Multi-Head Attention***](#multi-head-attention)
        + [***FIRST ADD & NORM (after attention)***](#first-add--norm-after-attention)
        + [***FEED‑FORWARD NETWORK (FFN)***](#feed%E2%80%91forward-network-ffn)
        + [***Then SECOND ADD & NORM — but you asked up to FFN output)***](#then-second-add--norm--but-you-asked-up-to-ffn-output)
- [What Problems Can You Solve?](#what-problems-can-you-solve)

<!-- tocstop -->

## Transformer Full Architecture

### Encoder

#### ***Input Layer***

**Token Embedding**
  - *Notation :-* X (shape: [seq_len, d_model])
  - *What :-* Converts each token in to a dense vector(non-zero. all carries a specific piece of information.) 
  - *Why :-* Neural networks need continuous vectors, not discrete IDs.
  - *How :-* Learnable lookup table (vocab_size × d_model) *nn.embedding*.
  - ***How Learnable Lookup or nn.Embedding***

**Positional Encoding**
  - *Notation :-* PE (same shape as X)
  - *What :-* Adds information about position (order) of tokens. 
  - *Why :-* Self‑attention is permutation‑invariant; without position info, “hello world” = “world hello”. *Bi-Directional*  
  - *How :-* Sinusodial functions or learnable embeddings, added elementwise x' = x + PE. Using sin and cos in every alternate dimension. Sine is applied to even-indexed dimensions, cosine to odd-indexed dimensions of the PE vector.

**Embedding + Positional Encoding: Without positional encoding, “I love you” = “you love I” to the model.**

`#### ***Multi-Head Attention***
  - **Linear Projections to QKV**
      - *Notation :-* Q = X'·W_Q,  K = X'·W_K,  V = X'·W_V
      - *Shape :-* W_Q, W_K, W_V are [d_model, d_k]; d_k = d_model / num_heads.
      - *What :-* Create three different representations from the same input
      - *Why :-* Query (what to look for), Key (what can be attended), Value (what to extract)
      - *Note :-* Each head has its own W_Q, W_K, W_V.

  - **Split into heads**
      - *Notation :-* Q → [num_heads, seq_len, d_k] (and same for K, V)
      - *What :-* Reshape and transpose to process heads in parallel.
      - *Why :-* Different heads can attend to different relationships (e.g., syntax, coreference).
  
  - **Scaled Dot‑Product Attention per head**
    - **Scores :- ** S = (Q·Kᵀ) / √d_k
      - *What :-*  Dot product between every query and every key.
      - *Why :-* Measures similarity (attention weight).
      - *√d_k:-* Scales down to prevent large dot products pushing softmax into saturated region. If we have [10, 1] than it represents [0.99, 0.01] after softmax. After scaling the same will be [0.73, 0.27].
      - *Padding Mask:-* Sentences are padded with 0 to match sequence length. Before softmax, PAD positions in the attention score matrix are set to −∞ so they become ~0 after softmax and contribute nothing to the output.
		 
    - **Weights :- ** A = softmax(S)   (applied row‑wise)
      - *What :-* Normalised attention probabilities over keys for each query.
      - *Why :-* To convert raw dot‑product scores (which can be any real number) into a probability distribution 
    - **Output :- ** head_out = A · V
       - *What :-* Weighted sum of values.
       - *Why :-* Attend to relevant positions and aggregate their information.
    - **Concatenate heads**
      - *Notation :-* concat = [head₁_out, head₂_out, ..., head_h_out]
      - *Shape :-*  [seq_len, d_model] (since h * d_k = d_model)
    - **Output projection**
      - *Notation :-* attn_out = concat · W_O 
      - *Shape :-*  W_O is [d_model, d_model]
       - *What :-* Linear transformation after concatenation.
	       - *Why :-* Mix information from different heads and project back to d_model.

**Multi‑head attention: Single‑head attention is a special case; multiple heads capture different linguistic patterns.**
**Scaling by √d_k: Prevents dot products from becoming too large, which would push softmax into extremely small gradients.**


#### ***FIRST ADD & NORM (after attention)***
  - **Residual connection**
- Tiny gradient = tiny slope = optimizer takes microscopic steps = no convergence
Residual = guarantees a minimum gradient of 1 = slope stays meaningful = learning continues
      - *Notation :-* attn_res = X' + attn_out
      - *What :-* Add the original input (from step 1) to the attention output.
      - *Why :-* Helps gradients flow through many layers (differnet encoders. We have 6 in original paper); mitigates vanishing gradient. So during backprop, the gradient has to travel backward through: FFN → Add&Norm → MHA → Add&Norm → FFN → Add&Norm → MHA → ... repeated N times. Each operation multiplies the gradient by some value less than 1, and after 6 blocks that's a lot of sequential multiplication — the signal degrades.

  - **Layer Normalization**
      - *Notation :-* norm1 = LayerNorm(attn_res)
      - *What :-* Normalises across feature dimension (d_model) to mean 0, variance 1, then scales/shifts. This comes all data points around mean where mean is 0 after normalization. It helps smooth gradients and faster convergence
      - *Why :-* Stabilises training, allows higher learning rates.

**Residual connections: Essential for training deep networks (>10 layers). Without them, training collapses.**

**Layer Normalization: Faster convergence than batch norm for sequences; works per sample, not per batch.**

#### ***FEED‑FORWARD NETWORK (FFN)***

This framing slightly undersells attention. Both attention and FFN learn representations — they just do different things. A more accurate framing: attention decides which information to mix across tokens; FFN applies nonlinear transformation to each token's mixed representation independently. Geva et al. (2021) — which is in your references — showed FFN layers act as key-value memory, where the first layer detects patterns and the second retrieves associated content. That's interview-level depth.

  - **First Linear Layer (expansion)**
    - *Notation :-* hidden = ReLU(norm1·W₁ + b₁)
    - *Shape :-*  W₁: [d_model, d_ff] (d_ff usually 4×d_model), b₁: [d_ff]
    - *What :-* Project to higher dimension. Adding non-Linearity.
    - *Why :-* without the FFN, the model has no position-wise nonlinearity — attention can only do weighted averaging of V, which limits representational power. Gives capacity to learn non‑linear features per position by adding activation ReLU / GeLU. Without expansion, FFN would be too weak.
    - *Activation :-* ReLU (or GELU) adds non‑linearity.
  - **Second Linear Layer (projection back)**
    - *Notation :- * ffn_out = hidden·W₂ + b₂
    - *Shape :- *  W₂: [d_ff, d_model], b₂: [d_model]
    - *What :- * Project back to d_model.
    - *Why :- * Return to the model’s internal dimension for the next block or output.

**FFN expansion (d_ff >> d_model): Gives the model “thinking capacity” after mixing information via attention. Without it, the model is just a series of linear+softmax operations.**

#### ***Then SECOND ADD & NORM — but you asked up to FFN output)***
  - *Notation :-*  ffn_res = norm1 + ffn_out   ← norm1 here is the FFN's input, which is correct
encoder_out = LayerNorm(ffn_res)
  - *Note :-* Same residual + layer norm pattern repeats after FFN.
Two reasons:

    Second residual path – gives gradients an alternative route around the FFN, preventing the FFN from becoming a bottleneck. Without it, deep models would struggle to train.

    Stabilise the next block’s input – after FFN, the distribution may have shifted. LayerNorm re‑centres and re‑scales so that the next encoder block (or decoder) receives well‑behaved inputs.

Pattern: Every sub‑layer (attention, FFN) is wrapped with Add → LayerNorm. This is the hallmark of the Transformer architecture and is critical for training stability at scale.

## What Problems Can You Solve?

***With a from-scratch Transformer***

|Problem|Example|
| --------------- | --------------- | 
|Sequence-to-sequence|Simple machine translation (e.g. English → French on a small dataset)|
|Text summarization (toy)| Abstractive summary on short paragraphs|
|Simple chatbot| Response generation on a small dialogue dataset|


Project 1 (Path A — 1 week): Build a minimal Transformer in PyTorch for English→French translation on the Multi30k dataset. Don't aim for good BLEU scores. Aim for a clean, readable implementation where you can point to every component and explain it. This becomes a strong interview talking point.



| Problem Type               | Models                          | Example Task                                                      |
|----------------------------|---------------------------------|-------------------------------------------------------------------|
| Text Classification        | BERT, DistilBERT                | Sentiment, spam detection, topic labeling                         |
| Named Entity Recognition   | BERT                            | Extract names, dates, org names from text                         |
| Question Answering         | BERT, RoBERTa                   | "Given this paragraph, answer this question"                      |
| Summarization              | T5, BART                        | Summarize news articles or documents                              |
| Text Generation            | GPT-2, GPT-Neo                  | Complete prompts, generate structured text                        |
| Translation                | MarianMT, T5                    | Language pairs                                                    |
| Semantic Search            | Sentence-BERT                   | Find similar documents, semantic similarity                       |

Project 2 (Path B — 2–3 weeks): Fine-tune DistilBERT for a classification task. The reason to start with DistilBERT over full BERT is purely practical — it's faster to train on Colab's free tier. Pick a task that connects to your P2P background if possible. For example: classifying financial news sentiment, or detecting clause types in loan agreement text. A generic IMDb sentiment classifier is fine too but less memorable.
Project 2 is what you'd actually show in a portfolio or talk about in an interview for an Applied NLP role.


























































