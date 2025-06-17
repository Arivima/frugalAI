import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ClassifyRequest(BaseModel):
    user_claim: str = Field(..., strip_whitespace=True, min_length=1)

class ClassifyResponse(BaseModel):
    model_name: str
    user_claim: str
    category: str
    explanation : str

class FeedbackRequest(BaseModel):
    user_claim: str = Field(..., strip_whitespace=True, min_length=1)
    predicted_category: int = Field(..., ge=0, le=7)
    assistant_explanation: str = Field(..., strip_whitespace=True, min_length=1)
    correct_category: int = Field(..., ge=0, le=7)


