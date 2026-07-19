"""Pydantic request/response models for the Document Analyzer API."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    invoice = "invoice"
    resume = "resume"
    contract = "contract"
    email = "email"
    other = "other"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw document text to analyze.")
    language: str = Field("auto", description="ISO code or 'auto' to detect.")
    summarize: bool = Field(True, description="Return a short summary.")


class Entity(BaseModel):
    label: str = Field(..., description="Entity type, e.g. PERSON, ORG, DATE, AMOUNT.")
    value: str


class AnalyzeResponse(BaseModel):
    document_type: DocumentType
    language: str
    summary: Optional[str] = None
    entities: List[Entity] = []
    sentiment: Optional[str] = Field(
        None, description="positive | neutral | negative for free-text documents."
    )
    token_usage: int = 0
