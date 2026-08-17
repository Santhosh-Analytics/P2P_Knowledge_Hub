from pydantic_settings import (
    BaseSettings,
)


class RerankerSettings(BaseSettings):
    provider: str = "sentence_transformers"
    model_name: str = "cross-encoder/ms-marco-MiniLM-L6-v2"
    candidate_k: int = 20
    top_k: int = 5
