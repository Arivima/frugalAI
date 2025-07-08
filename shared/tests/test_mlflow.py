import mlflow.sklearn
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from shared.config import setup_logging
from shared.mlflow_utils import mlflow_log_model, mlflow_track, mlflow_load_model


def test_mlflow():
    setup_logging()

    # Test with safe mode (default)
    @mlflow_track(experiment_name="test")
    def test_train(X, y):
        """blabla"""
        clf = RandomForestClassifier()
        clf.fit(X, y)
        mlflow_log_model(
            model=clf,
            name="model",
            registered_model_name="model"
            )
        return clf

    X, y = make_classification(n_samples=100, n_features=4)
    clf = test_train(X, y)
    print(f"clf: {clf}")


    loaded_model = mlflow_load_model("models:/model/latest")
    test_prediction = loaded_model.predict(X[:1])

    print(f"Test prediction: {test_prediction}, x {X[:1]} y {y[:1]}")
