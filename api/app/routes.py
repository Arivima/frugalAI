"""
API router for model operations and feedback collection.

This module defines the FastAPI endpoints used to:
- (`GET /`)              Check API and model status 
- (`GET /reload_model`)  Triggers a model adapter reload from GCS 
- (`POST /classify`)     Classify a user claim using the model 
- (`POST /feedback`)     Send user feedback to BQ 

Requires shared modules
"""

import logging
from pydantic import BaseModel, Field
from fastapi import (
    APIRouter, 
    Request, 
    Response,
    HTTPException, 
    status,
    )
from shared.pydantic_models import (
    ClassifyRequest, 
    ClassifyResponse,
    FeedbackRequest
    )
from shared.gcp import Gcp
from shared.config import Config
from app.model import LLMWrapper



logger = logging.getLogger(__name__)

router = APIRouter()



@router.get("/")
async def root(request: Request):
    """Check API and model status """
    model_loaded = hasattr(request.app.state, "model") and getattr(request.app.state, "model") is not None
    return {"status": "ok", "model_loaded": model_loaded}

@router.get("/reload_model")
async def reload(request: Request):
    """Triggers a model adapter reload from GCS"""
    try:
        logger.info("New reload request")
        Gcp.load_adapter_gcs(
            project_id=Config.GCP_PROJECT_ID,
            bucket_name=Config.GCS_BUCKET_NAME,
            adapter_name=Config.ADAPTER_NAME,
            local_directory=Config.LOCAL_DIRECTORY,
        )
        request.app.state.model = LLMWrapper()
        return {"reload": "ok"}
    except Exception as e:
        logger.exception("Error reloading model: %s", e)
        raise HTTPException(status_code=500, detail="Error reloading model") from e

@router.post("/classify", response_model=ClassifyResponse, tags=["classification"])
async def classify(request: Request, body: ClassifyRequest):
    """Classifies a user claim using the currently loaded LLM model."""
    logger.info("New classification request: %s", body)

    llm = getattr(request.app.state, "model", None)
    if llm is None:
        logger.error("Model not available")
        raise HTTPException(status_code=500, detail="Model not available")
    logger.info("Model available")

    try:
        category, explanation = llm.generate(quote=body.user_claim)
    except Exception as e:
        logger.exception("Error during generation: %s", e)
        raise HTTPException(status_code=500, detail=f"Error during generation: {e}") from e

    response_data = {
        "model_name":   llm.model_name,
        "user_claim":   body.user_claim,
        "category":     category,
        "explanation":  explanation
    }
    logger.info("response: %s", response_data)
    return ClassifyResponse(**response_data)


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT, tags=["feedback"])
async def submit_feedback(request: Request, body: FeedbackRequest):
    """Send user feedback to BQ """

    logger.info("New feedback request: %s", body)

    Gcp.send_feedback_bq(
        project_id=Config.GCP_PROJECT_ID,
        dataset_id=Config.BQ_DATASET_ID,
        table_id=Config.BQ_TABLE_ID,
        user_claim=body.user_claim,
        predicted_category=int(body.predicted_category),
        assistant_explanation=body.assistant_explanation,
        correct_category=int(body.correct_category)
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

