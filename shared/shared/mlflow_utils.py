import functools
import logging

import mlflow
from codecarbon import EmissionsTracker

from shared.config import Config, setup_logging

logger = logging.getLogger(__name__)

mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)


def mlflow_track(experiment_name: str = "default"):
    """
    Decorator to track a function in an MLflow run.
    Automatically logs params and metrics
    Additionally logs execution time and carbon emissions.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mlflow.set_experiment(experiment_name)
            tracker = EmissionsTracker(
                project_name="frugalai",
                measure_power_secs=1,
                save_to_file=False,
            )
            with mlflow.start_run(run_name=func.__name__):
                mlflow.autolog()

                tracker.start()
                result = func(*args, **kwargs)
                tracker.stop()

                for key, value in vars(tracker.final_emissions_data).items():
                    mlflow.log_metric(f"codecarbon_{key}", value)

                mlflow.log_metric("duration", tracker.final_emissions_data.duration)
                mlflow.log_metric("return_value", result)

                return result

        return wrapper

    return decorator


# def mlflow_log_model(model, artifact_path: str, registered_model_name: str = None):
#     """
#     Log a PyTorch model (e.g., LLM adapter) to MLflow.
#     """
#     try:
#         logger.info("Logging model to MLflow at: %s", artifact_path)
#         mlflow.set_experiment("model-logging")

#         with mlflow.start_run():
#             mlflow.pytorch.log_model(model, artifact_path=artifact_path)

#             if registered_model_name:
#                 mlflow.register_model(
#                     f"runs:/{mlflow.active_run().info.run_id}/{artifact_path}",
#                     registered_model_name,
#                 )

#         logger.info("✅ Model logged to MLflow")
#     except Exception as e:
#         logger.exception("❌ Failed to log model to MLflow: %s", e)


# def mlflow_load_model(model_uri: str):
#     """
#     Load a model from MLflow (by URI).
#     Example URI: 'models:/my-model-name/production'
#     """
#     try:
#         logger.info("Loading model from MLflow: %s", model_uri)
#         model = mlflow.pytorch.load_model(model_uri)
#         return model
#     except Exception as e:
#         logger.exception("❌ Error loading model from MLflow: %s", e)
#         raise


if __name__ == "__main__":
    setup_logging()

    print("Config.MLFLOW_TRACKING_URI", Config.MLFLOW_TRACKING_URI)
