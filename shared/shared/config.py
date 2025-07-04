import logging
import os

class Config:
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
    GCP_REGION = os.getenv("GCP_REGION", "")
    BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "")
    BQ_TABLE_ID = os.getenv("BQ_TABLE_ID", "")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
    LOCAL_DIRECTORY = os.getenv("LOCAL_DIRECTORY", "")
    ADAPTER_NAME = os.getenv("ADAPTER_NAME", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
