"""Pydantic request/response models for the API."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000, examples=[
        "My payment failed twice and I was still charged, this is urgent!"
    ])
    subject: str | None = Field(default=None, max_length=200)


class ClassificationResponse(BaseModel):
    category: str
    category_confidence: float
    priority: str
    model_suggested_priority: str
    model_confidence: float
    reasons: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
