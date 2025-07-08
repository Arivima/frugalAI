"""
API router for model operations and feedback collection.

This module defines the FastAPI endpoints used to:
- (`GET /`)              Check API status
- (`GET /health`)        Vertex AI endpoint for healthcheck - healthy when model is loaded
- (`GET /reload_model`)  Triggers a model adapter reload from GCS
- (`POST /predict`)      Classify a user claim using the model - uses Vertex AI convention
- (`POST /feedback`)     Send user feedback to BQ

Requires shared modules
"""

import logging

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    status,
)

from shared.config import Config
from shared.gcp import Gcp
from shared.model.model import LLMWrapper
from shared.pydantic_models import (
    ClassifyRequest, 
    ClassifyResponse, 
    FeedbackRequest,
    PredictRequest,
    PredictResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """healthcheck api"""
    return {"status": "ok"}


# documentation https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements
@router.get("/health")
async def health(request: Request):
    """Vertex AI healthcheck endpoint — only return 200 when model is ready"""
    model_loaded = (
        hasattr(request.app.state, "model")
        and getattr(request.app.state, "model") is not None
    )
    return Response(status_code=200 if model_loaded else 503)


@router.get("/reload_model")
async def reload(request: Request):
    """External force reload : triggers a model adapter reload from GCS"""
    try:
        logger.info("New reload request")
        if (
            hasattr(request.app.state, "model")
            and getattr(request.app.state, "model") is not None
        ):
            request.app.state.model.clear()
        Gcp.load_adapter_gcs(
            project_id=Config.GCP_PROJECT_ID,
            bucket_name=Config.GCS_BUCKET_NAME,
            adapter_name=Config.ADAPTER_NAME,
            local_directory=Config.LOCAL_DIRECTORY,
        )
        request.app.state.model = LLMWrapper(
            local_directory=Config.LOCAL_DIRECTORY,
            adapter_name=Config.ADAPTER_NAME,
            model_name=Config.MODEL_NAME,
            project_id=Config.GCP_PROJECT_ID,
            bucket_name=Config.GCS_BUCKET_NAME,
        )
        return {"reload": "ok"}

    except Exception as e:
        logger.exception("Error reloading model: %s", e)
        raise HTTPException(status_code=500, detail="Error reloading model") from e



@router.post("/predict", response_model=PredictResponse, tags=["classification"])
async def predict(request: Request, body: PredictRequest):
    """
    Classify a list of user claims using the loaded LLM model.
    Vertex AI expects a POST to /predict with: {"instances": [{"text": "..."}]}
    Returns: {"predictions": [...]} with a list of responses.
    """
    logger.info("New classification request with %d instances", len(body.instances))
    logger.info("user_claim %s", body.instances[0].user_claim)

    llm = getattr(request.app.state, "model", None)
    if llm is None:
        logger.error("Model not available")
        raise HTTPException(status_code=500, detail="Model not available")
    logger.info("Model available")

    responses = []
    for instance in body.instances:
        try:
            category, explanation = llm.generate(quote=instance.user_claim)
            responses.append(ClassifyResponse(
                model_name=llm.model_name,
                user_claim=instance.user_claim,
                category=category,
                explanation=explanation
            ))
            logger.info("response: %s", responses[-1])

        except Exception as e:
            logger.exception("Error during generation: %s", e)
            raise HTTPException(
                status_code=500,
                detail=f"Error during generation: {e}"
            ) from e

    return PredictResponse(predictions=responses)



@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT, tags=["feedback"])
async def submit_feedback(request: Request, body: FeedbackRequest):
    """Send user feedback to BQ"""

    logger.info("New feedback request: %s", body)

    Gcp.send_feedback_bq(
        project_id=Config.GCP_PROJECT_ID,
        dataset_id=Config.BQ_DATASET_ID,
        table_id=Config.BQ_TABLE_ID,
        user_claim=body.user_claim,
        predicted_category=int(body.predicted_category),
        assistant_explanation=body.assistant_explanation,
        correct_category=int(body.correct_category),
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
