import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# API
class ClassifyRequest(BaseModel):
    user_claim: str = Field(
        ..., strip_whitespace=True, min_length=1, example="Climate change is cool"
    )


class ClassifyResponse(BaseModel):
    model_name: str
    user_claim: str = Field(
        ..., strip_whitespace=True, min_length=1, example="Climate change is cool"
    )
    category: str
    explanation: str


class FeedbackRequest(BaseModel):
    user_claim: str = Field(..., strip_whitespace=True, min_length=1)
    predicted_category: int = Field(..., ge=0, le=7)
    correct_category: int = Field(..., ge=0, le=7)
    assistant_explanation: Optional[str] = Field(
        ..., strip_whitespace=True, min_length=1
    )


# BQ
class FeedbackInsertionBQ(FeedbackRequest):
    created_at: datetime  # TIMESTAMP
