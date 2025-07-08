import functools
import logging
import os

import mlflow
from codecarbon import EmissionsTracker

from shared.config import Config, setup_logging

logger = logging.getLogger(__name__)

# limit timeout
os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "30"
os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = "3"


def mlflow_track(experiment_name: str = "default"):
    """
    Decorator to track a function in an MLflow run.
    Automatically logs params and metrics
    Additionally logs execution time and carbon emissions.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
                logger.info("Connected to %s", Config.MLFLOW_TRACKING_URI)

                logger.info("creds %s", Config.GOOGLE_APPLICATION_CREDENTIALS)

                mlflow.set_experiment(experiment_name)
                logger.info("Experiment %s", experiment_name)

                with mlflow.start_run() as run:
                    logger.info("Run name %s", run.info._run_name)

                    mlflow.autolog()

                    tracker = EmissionsTracker(
                        project_name="frugalai",
                        measure_power_secs=1,
                        save_to_file=False,
                        log_level='error'
                    )
                    tracker.start()
                    _result = func(*args, **kwargs)
                    tracker.stop()

                    for key, value in vars(tracker.final_emissions_data).items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(f"codecarbon_{key}", value)
                        else:
                            mlflow.log_param(f"codecarbon_{key}", value)

                    mlflow.log_metric("duration", tracker.final_emissions_data.duration)

                    return _result

            except Exception as e:
                logger.error("MLflow tracking failed for %s : %s", func.__name__, e)
                raise

        return wrapper

    return decorator


def mlflow_log_model(model, name: str, registered_model_name: str = None):
    """
    Log a PyTorch model (e.g., LLM adapter) to MLflow.
    """
    try:
        # mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
        # logger.info("Connected to %s", Config.MLFLOW_TRACKING_URI)

        mlflow.sklearn.log_model(model, name=name)

        if registered_model_name:
            mlflow.register_model(
                f"runs:/{mlflow.active_run().info.run_id}/{name}",
                registered_model_name,
            )

        logger.info("✅ Model logged to MLflow")
        return True

    except Exception as e:
        logger.error("❌ Failed to log model: %s", e)
        return False


def mlflow_load_model(model_uri: str):
    """
    Load a model from MLflow

    Args:
        model_uri: MLflow model URI (e.g., 'models:/my-model-name/production')
    """
    try:
        mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
        logger.info("Loading model from MLflow: %s", model_uri)
        model = mlflow.sklearn.load_model(model_uri)
        logger.info("✅ Model loaded successfully")
        return model

    except Exception as e:
        logger.error("❌ Error loading model from MLflow: %s", e)
        raise


