import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from shared.config import setup_logging, Config
from shared.gcp import Gcp
from app.routes import router
from app.model import LLMWrapper

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for FastAPI - triggered at startup and shutdown.
    - Downloads model adapter files from Google Cloud Storage.
    - Initializes a model into the app state.
    - Clears the model from memory on shutdown.
    """
    logger.info('Starting API')
    try:
        Gcp.load_adapter_gcs(
            project_id=Config.GCP_PROJECT_ID,
            bucket_name=Config.GCS_BUCKET_NAME,
            adapter_name=Config.ADAPTER_NAME,
            local_directory=Config.LOCAL_DIRECTORY,
        )
        app.state.model = LLMWrapper()

    except Exception as e:
        logger.exception(f"{e}")

    yield

    if app.state.model is not None:
        app.state.model.clear()
    logger.info("Shutting down API")


app = FastAPI(lifespan=lifespan)
setup_logging()
app.include_router(router)
