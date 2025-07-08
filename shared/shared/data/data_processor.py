# - load from BQ
# - preprocess
# - train test split
# - tokenization

import logging

from datasets import ClassLabel, Dataset

from shared.config import Config, setup_logging
from shared.gcp import Gcp

logger = logging.getLogger(__name__)


# USE SCHEMA VALIDATION
class DataProcessor:
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        start_date: str,
    ):
        logger.info("Loading training dataset from bq")
        self.df = Gcp.load_data_bq(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            start_date=start_date,
        )
        self.ds = Dataset.from_pandas(self.df)
        self.train_ds = None
        self.test_ds = None

    def create_splits(self, test_size=0.2):
        logger.info("create_splits")

        try:
            if not isinstance(self.ds.features["label_true"], ClassLabel):
                unique_labels = sorted(self.ds.unique("label_true"))
                class_label = ClassLabel(names=unique_labels)
                self.ds = self.ds.cast_column("label_true", class_label)

            split1 = self.ds.train_test_split(
                test_size=test_size, seed=0, stratify_by_column="label_true"
            )

            self.train_ds = split1["train"]
            self.test_ds = split1["test"]

            return self.train_ds, self.test_ds

        except Exception as e:
            logger.error(f"Error in create_splits: {e}")
            raise


if __name__ == "__main__":
    setup_logging()

    data = DataProcessor(
        project_id=Config.GCP_PROJECT_ID,
        dataset_id=Config.BQ_DATASET_ID,
        table_id=Config.BQ_TABLE_ID,
        start_date=None,
    )
    data.create_splits()
    print(data.df.shape, data.ds.shape, data.train_ds.shape, data.test_ds.shape)
