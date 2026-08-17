from pydantic import BaseModel
from enum import StrEnum


class QueryRequest(BaseModel):
    query: str
