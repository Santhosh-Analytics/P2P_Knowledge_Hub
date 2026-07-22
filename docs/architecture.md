Settings → Logger → Exceptions → Hashing → Deduplication

models/
├── domain/
│ └── document.py ← Pydantic
│
└── db/
├── base.py ← DeclarativeBase only
├── session.py
└── document.py ← SQLAlchemy ORM
