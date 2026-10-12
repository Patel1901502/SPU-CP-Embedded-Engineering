"""Reproducible training artifacts and explicit inference stream state."""

import hashlib
import platform
from dataclasses import dataclass
from importlib.metadata import version

import joblib
from sklearn.ensemble import IsolationForest

from .features import FEATURE_COLUMNS, feature_matrix

ARTIFACT_VERSION = 1


@dataclass
class ModelArtifact:
    estimator: IsolationForest
    metadata: dict


def train_model(dataframe, *, n_estimators=100, contamination=0.03, random_state=42):
    if not isinstance(random_state, int):
        raise ValueError("random_state must be an integer for reproducible training")
    features = feature_matrix(dataframe)
    estimator = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=1,
    ).fit(features)
    metadata = {
        "artifact_version": ARTIFACT_VERSION,
        "feature_order": list(FEATURE_COLUMNS),
        "training_parameters": estimator.get_params(),
        "training_samples": len(features),
        "training_sha256": hashlib.sha256(features.to_csv(index=False).encode()).hexdigest(),
        "temperature_delta_policy": "row-order; zero at recording start; carry explicit stream state",
        "versions": {name: version(name) for name in ("numpy", "pandas", "scikit-learn", "joblib")},
        "python_version": platform.python_version(),
    }
    return ModelArtifact(estimator, metadata)


def validate_artifact(model):
    if not isinstance(model, ModelArtifact):
        raise ValueError("Legacy model lacks reproducibility metadata; retrain with embedded-train")
    if model.metadata.get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("Unsupported model artifact version")
    if list(model.estimator.feature_names_in_) != model.metadata.get("feature_order"):
        raise ValueError("Model feature order disagrees with saved metadata")
    return model


def save_model(model, path):
    joblib.dump(validate_artifact(model), path)


def load_model(path):
    """Load only trusted artifacts: joblib can execute code during loading."""
    return validate_artifact(joblib.load(path))


def score_samples(model, dataframe, *, previous_temp=None):
    """Score an independent recording unless previous_temp is supplied."""
    model = validate_artifact(model)
    features = feature_matrix(
        dataframe, previous_temp=previous_temp, feature_order=model.metadata["feature_order"]
    )
    output = dataframe.copy()
    output["temp_delta"] = features["temp_delta"].to_numpy()
    predictions = model.estimator.predict(features)
    output["anomaly"] = ["NORMAL" if value == 1 else "ANOMALY" for value in predictions]
    output["score"] = model.estimator.decision_function(features)
    return output


class InferenceSession:
    """One ordered stream: carry last temperature across successful batches.

    reset() starts an independent recording. Invalid batches do not advance state.
    Use a separate instance per device/recording; do not interleave streams.
    """

    def __init__(self, model, *, previous_temp=None):
        self.model = validate_artifact(model)
        self.previous_temp = previous_temp

    def reset(self):
        self.previous_temp = None

    def score(self, dataframe):
        output = score_samples(self.model, dataframe, previous_temp=self.previous_temp)
        self.previous_temp = float(dataframe["temp_c"].iloc[-1])
        return output
