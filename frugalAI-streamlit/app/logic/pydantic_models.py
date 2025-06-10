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
