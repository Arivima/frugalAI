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
from app.gcp import send_feedback_bq, load_model_gcs
from app.model import LLMWrapper



logger = logging.getLogger(__name__)

router = APIRouter()



@router.get("/")
async def root(request: Request):
    model_loaded = hasattr(request.app.state, "model") and getattr(request.app.state, "model") is not None
    return {"status": "ok", "model_loaded": model_loaded}

@router.get("/reload_model")
async def reload(request: Request):
    try:
        logger.info("New reload request")
        load_model_gcs()
        request.app.state.model = LLMWrapper()
        return {"reload": "ok"}
    except Exception as e:
        logger.exception(f"Error reloading model: {e}")
        raise HTTPException(status_code=500, detail="Error reloading model")

@router.post("/classify", response_model=ClassifyResponse, tags=["classification"])
async def classify(request: Request, body: ClassifyRequest):

    logger.info(f"New classification request : {body}")

    llm = getattr(request.app.state, "model", None)
    if llm is None:
        logger.error(f"Model not available")
        raise HTTPException(status_code=500, detail="Model not available")
    logger.info(f"Model available")

    try:
        category, explanation = llm.generate(quote=body.user_claim)
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        raise HTTPException(status_code=500, detail=f"Error during generation: {e}")

    response_data = {
        "model_name":   llm.model_name,
        "user_claim":   body.user_claim,
        "category":     category,
        "explanation":  explanation
    }
    logger.info(f"response: {response_data}")
    return ClassifyResponse(**response_data)


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT, tags=["feedback"])
async def submit_feedback(request: Request, body: FeedbackRequest):

    logger.info(f"New feedback request : {body}")

    send_feedback_bq(
        user_claim=body.user_claim,
        predicted_category=int(body.predicted_category),
        assistant_explanation=body.assistant_explanation,
        correct_category=int(body.correct_category)
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

