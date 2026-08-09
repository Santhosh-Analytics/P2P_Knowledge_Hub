<div align="center">

# TicketIQ

**Multi-task NLP triage for customer support tickets — category, priority, and sentiment in a single forward pass.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)

![Framework](https://img.shields.io/badge/Model-RoBERTa+LoRA-orange?style=flat-square&logo=huggingface)

![API](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)

![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)

[Model Weights](https://huggingface.co/San-Analytics/TicketIQ-MultiTask) · [API Docs](#api-reference) · [Docker Hub](#docker) · [Live Demo](#)


</div>

---

## What It Does

TicketIQ takes a raw support ticket and returns three predictions simultaneously — no chained calls, no separate models.

| Task | Labels (examples) |
|---|---|
| **Category** | `account`, `billing`, `technical`, `shipping`, … |
| **Priority** | `low`, `medium`, `high`, `critical` |
| **Sentiment** | `positive`, `neutral`, `negative` |

A shared RoBERTa encoder (125M params, fine-tuned with LoRA) feeds three independent classification heads. Multi-task learning lets related tasks share linguistic representations — reducing inference cost, memory, and training time compared to three separate models.

---

## Quick Start

### Docker (recommended)

```bash
docker pull sananalytics/ticketiq
docker run -p 8000:8000 sananalytics/ticketiq
```

### From Source

```bash
git clone https://github.com/San-Analytics/TicketIQ
cd TicketIQ
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## API Reference

### `POST /predict` — Single ticket

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "My account has been locked and I cannot log in."}'
```

```json
{
  "category":             "account",
  "priority":             "high",
  "sentiment":            "negative",
  "category_confidence":  0.94,
  "priority_confidence":  0.88,
  "sentiment_confidence": 0.97
}
```


### Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/predict` | Single ticket inference |
| `POST` | `/predict/batch` | Batch inference (list of texts) |
| `GET` | `/health` | Liveness check |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/demo` | Gradio UI |

---

## Architecture

```
                        ┌─────────────────┐
                        │ Raw Ticket Text │
                        └────────┬────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Data Pipeline         │
                    │  Clean → Label → Split │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │  RoBERTa Tokenizer     │
                    └────────┬───────────────┘
                             │
                             ▼
          ┌────────────────────────────────────────┐
          │  RoBERTa Encoder (125M) + LoRA Adapters│
          └──────────┬────────────┬────────────────┘
                     │            │            │
                     ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Category │ │ Priority │ │Sentiment │
              │   Head   │ │   Head   │ │   Head   │
              └────┬─────┘ └────┬─────┘ └────┬─────┘
                   └────────────┴─────────────┘
                                │
                                ▼
                    ┌────────────────────┐
                    │  TicketPrediction  │
                    │  (JSON response)   │
                    └────────┬───────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   FastAPI Service  │
                    └────────────────────┘
```

**Why multi-task?** Rather than training three independent models, TicketIQ shares a single encoder across all three tasks. Related tasks (priority and sentiment both benefit from understanding urgency language) reinforce each other through shared representations, while task-specific heads keep predictions independent.

---

## Model Details

| Attribute | Value |
|---|---|
| Base model | `roberta-base` — 125M parameters |
| Fine-tuning | LoRA (Low-Rank Adaptation) — parameter-efficient |
| Tasks | Category, Priority, Sentiment |
| Architecture | Shared encoder + 3 independent classification heads |
| Inference | Single forward pass for all three outputs |

**Model on Hugging Face:** [`San-Analytics/TicketIQ-MultiTask`](https://huggingface.co/San-Analytics/TicketIQ-MultiTask)

---

## Project Structure

```
TicketIQ/
├── app/
│   ├── main.py          # FastAPI app + routes
│   ├── model.py         # Model loading + inference
│   └── schemas.py       # Pydantic request/response schemas
├── training/
│   ├── train.py         # Multi-task training loop
│   ├── dataset.py       # Data pipeline, cleaning, labeling
│   └── config.toml      # Hyperparameters
├── demo/
│   └── app.py           # Gradio demo (optional)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Gradio Demo (optional)

A minimal Gradio app is included under `demo/` for quick interactive testing without curl.

```bash
pip install gradio
python demo/app.py
```

---

## License

MIT
