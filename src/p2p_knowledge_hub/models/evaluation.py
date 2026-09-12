from uuid import UUID
from pydantic import BaseModel, Field
from enum import StrEnum


class P2PCategory(StrEnum):
    supplier = "Supplier"
    po = "PurchaseOrder"
    inv = "Invoice"
    payment = "Payment"


class Evaluation(BaseModel):
    query: str = Field(min_length=1)
    correct_document_id: list[UUID] = Field(min_length=1)  # document recall
    correct_chunk_id: list[UUID] = Field(min_length=1)  # chunk recall
    reference_answer: str = Field(min_length=1)
    category: P2PCategory
