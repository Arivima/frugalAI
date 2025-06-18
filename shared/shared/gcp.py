# TODO
# add tests

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from google.cloud import bigquery, storage
from google.cloud.exceptions import GoogleCloudError
from google.cloud.storage import transfer_manager

from shared import pydantic_models, utils

logger = logging.getLogger(__name__)


class Gcp:
    @staticmethod
    def load_adapter_gcs(
        project_id: str,
        bucket_name: str,
        adapter_name: str,
        local_directory: str,
    ) -> Optional[str]:
        """
        Downloads adapter files from a specified GCS bucket to a specified local directory.

        Args:
            project_id (str): Google Cloud project ID.
            bucket_name (str): Name of the GCS bucket.
            adapter_name (str): Prefix name of the adapter folder in GCS.
            local_directory (str): Local directory path where files will be saved.

        Returns:
            Optional[str]: The local directory path if the download succeeds, else None.

        Raises:
            GoogleCloudError: If a GCS-related error occurs.
            Exception: For any unexpected errors.
        """
        try:
            logger.info("📍 load_adapter_gcs")

            utils.validate_required_fields(
                project_id=project_id,
                bucket_name=bucket_name,
                adapter_name=adapter_name,
                local_directory=local_directory,
            )

            client = storage.Client(project=project_id)
            logger.info("connected to client : %s", client.project)

            bucket = client.bucket(bucket_name)
            logger.info("connected to bucket : %s", bucket.name)

            prefix = adapter_name + "/"
            logger.info(f"Looking with prefix : {prefix}")
            blobs = list(bucket.list_blobs(prefix=prefix, delimiter="/"))
            logger.info(f"Number of blobs found: {len(blobs)}")
            if not blobs:
                raise ValueError("No files found")

            blob_names = [
                blob.name for blob in blobs if blob.name.startswith(f"{adapter_name}/")
            ]
            results = transfer_manager.download_many_to_path(
                bucket, blob_names, destination_directory=local_directory
            )

            for name, result in zip(blob_names, results):
                if isinstance(result, Exception):
                    logger.error(
                        "Failed to download %s due to exception: %s", name, result
                    )
                else:
                    logger.info("Downloaded %s.", os.path.join(local_directory, name))

            logger.info("✅ Adapter downloaded successfully from GCS.")
            return local_directory

        except GoogleCloudError as e:
            logger.error(f"❌ Error downloading adapter from GCS: {e}.")
            return None
        except Exception as e:
            logger.exception(f"❌ Unexpected error downloading adapter from GCS: {e}.")
            return None

    @staticmethod
    def load_data_bq(
        project_id: str,
        dataset_id: str,
        table_id: str,
        start_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Loads data from a BigQuery table into a pandas DataFrame.

        Args:
            project_id (str): Google Cloud project ID.
            dataset_id (str): BigQuery dataset ID.
            table_id (str): BigQuery table ID.
            start_date (Optional[str]): If provided, filters rows with a timestamp after this date.

        Returns:
            pd.DataFrame: DataFrame containing the queried rows with following fields:
            - 'text', 'label_pred', 'label_true', 'explanation', 'created_at'

        Raises:
            GoogleCloudError: If a BigQuery-related error occurs.
            Exception: For any unexpected errors.
        """
        try:
            logger.info("📍 load_data_bq")

            utils.validate_required_fields(
                project_id=project_id,
                dataset_id=dataset_id,
                table_id=table_id,
                optional={
                    "start_date": start_date,
                },
            )

            client = bigquery.Client(project=project_id)
            logger.info(f"BigQuery table : {project_id}.{dataset_id}.{table_id}")

            where_clause = f"WHERE timestamp > '{start_date}'" if start_date else ""
            query = f"""
            SELECT 
                user_claim as text,
                predicted_category as label_pred,
                correct_category as label_true,
                assistant_explanation as explanation,
                created_at
            FROM `{dataset_id}.{table_id}`
            {where_clause}
            """

            df = client.query(query).to_dataframe()
            df["text"] = df["text"].str.strip()

            logger.info(f"✅ Query successful, df shape {df.shape}")
            return df

        except GoogleCloudError as e:
            logger.error(f"❌ Error downloading data from BQ: {e}.")
            raise
        except Exception as e:
            logger.exception(f"❌ Unexpected error downloading data from BQ: {e}.")
            raise

    @staticmethod
    def send_feedback_bq(
        project_id: str,
        dataset_id: str,
        table_id: str,
        user_claim: str,
        predicted_category: int,
        correct_category: int,
        assistant_explanation: str = None,
    ) -> Optional[bool]:
        """
        Sends a feedback row to a BigQuery table after validating it with a Pydantic model.

        Args:
            project_id (str): Google Cloud project ID.
            dataset_id (str): BigQuery dataset ID.
            table_id (str): BigQuery table ID.
            user_claim (str): The user's input text.
            predicted_category (int): Category predicted by the model.
            correct_category (int): Correct category as labeled by the user.
            assistant_explanation (Optional[str]): Optional explanation text by the model.

        Returns:
            Optional[bool]: True if the row was inserted successfully; raises otherwise.

        Raises:
            GoogleCloudError: If a BigQuery-related error occurs.
            Exception: For any unexpected errors or validation failures.
        """
        try:
            logger.info("📍 send_feedback_bq")

            utils.validate_required_fields(
                project_id=project_id,
                dataset_id=dataset_id,
                table_id=table_id,
                user_claim=user_claim,
                predicted_category=predicted_category,
                correct_category=correct_category,
                optional={
                    "assistant_explanation": assistant_explanation,
                },
            )

            row_data = {
                "created_at": datetime.now(timezone.utc),
                "user_claim": user_claim,
                "predicted_category": predicted_category,
                "correct_category": correct_category,
                "assistant_explanation": assistant_explanation,
            }

            validated_row = pydantic_models.FeedbackInsertionBQ(**row_data)

            client = bigquery.Client(project=project_id)
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)
            logger.info("BigQuery table : %s", table)

            errors = client.insert_rows_json(
                table, [validated_row.model_dump(mode="json")]
            )

            if errors:
                logger.error(f"BigQuery insertion failed: {errors}")
                raise Exception(f"BigQuery insertion failed: {errors}")

            logger.info(
                f"✅ BigQuery insertion succeeded: {validated_row.model_dump()}"
            )
            return True

        except GoogleCloudError as e:
            logger.error(f"❌ Error inserting data to BQ: {e}.")
            raise
        except Exception as e:
            logger.exception(f"❌ Unexpected error inserting data to BQ: {e}.")
            raise


def test_gcp_pipeline(config: object):
    Gcp.load_data_bq(
        project_id=config.GCP_PROJECT_ID,
        dataset_id=config.BQ_DATASET_ID,
        table_id=config.BQ_TABLE_ID,
        start_date=None,
    )

    Gcp.load_adapter_gcs(
        project_id=config.GCP_PROJECT_ID,
        bucket_name=config.GCS_BUCKET_NAME,
        adapter_name=config.ADAPTER_NAME,
        local_directory=config.LOCAL_DIRECTORY,
    )

    Gcp.send_feedback_bq(
        project_id=config.GCP_PROJECT_ID,
        dataset_id=config.BQ_DATASET_ID,
        table_id=config.BQ_TABLE_ID,
        user_claim="user claim",
        predicted_category=6,
        correct_category=2,
        assistant_explanation="explanation",
    )


if __name__ == "__main__":
    from shared.config import Config, setup_logging

    setup_logging()

    try:
        test_gcp_pipeline(config=Config)
    except Exception as e:
        logger.exception(f"Error in gcp.py {e}")
