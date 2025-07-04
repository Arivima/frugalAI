import logging

from datasets import Dataset

from shared.data.data_processor import DataProcessor
from shared.config import Config, setup_logging
from shared.model.model import LLMWrapper

logger = logging.getLogger(__name__)


def load_new_data():
    data = DataProcessor(
        project_id=Config.GCP_PROJECT_ID,
        dataset_id=Config.BQ_DATASET_ID,
        table_id=Config.BQ_TABLE_ID,
        start_date=None,
    )
    data.create_splits()
    print(data.df.shape, data.ds.shape, data.train_ds.shape, data.test_ds.shape)
    print(data.df.columns)
    print(data.train_ds[0])
    return data


def retrain(data: Dataset):
    model = LLMWrapper(
        model_name=Config.MODEL_NAME,
        adapter_name=Config.ADAPTER_NAME,
        local_directory=Config.LOCAL_DIRECTORY,
        project_id=Config.GCP_PROJECT_ID,
        bucket_name=Config.GCS_BUCKET_NAME,
    )

    # train_metrics = model.train(data_train=data.train_ds, data_val=data.val_ds)

    return model


def evaluate(model, data: Dataset):
    eval_metrics = model.evaluate(
        data=data,
    )
    return eval_metrics

def workflow():
    data = load_new_data()
    model = retrain(data.train_ds)
    evaluate(model, data.test_ds)


if __name__ == "__main__":
    setup_logging()

    workflow()
