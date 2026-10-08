"""Callable ML operations independent of argument parsing and file I/O."""

from sklearn.ensemble import IsolationForest

from .features import feature_matrix


def train_model(dataframe, *, n_estimators=100, contamination=0.03, random_state=42):
    """Fit an anomaly detector with configurable training parameters."""
    model = IsolationForest(
        n_estimators=n_estimators, contamination=contamination, random_state=random_state
    )
    return model.fit(feature_matrix(dataframe))


def score_samples(model, dataframe):
    """Return a new frame with labels and scores, preserving the input index."""
    features = feature_matrix(dataframe)
    predictions = model.predict(features)
    output = dataframe.copy()
    output["anomaly"] = ["NORMAL" if value == 1 else "ANOMALY" for value in predictions]
    output["score"] = model.decision_function(features)
    return output
