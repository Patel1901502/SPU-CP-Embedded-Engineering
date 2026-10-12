import json
import subprocess
from importlib.resources import files

import numpy as np
import pandas as pd
import pytest

from ml.evaluate import evaluate_model
from ml.features import feature_matrix
from ml.model import InferenceSession, load_model, save_model, score_samples, train_model


@pytest.fixture
def training():
    return pd.read_csv(files("tools").joinpath("data/training.csv"))


@pytest.mark.parametrize("bad", ["missing", "nan", "infinite", "text", "empty", "duplicate"])
def test_invalid_telemetry(training, bad):
    if bad == "missing":
        training = training.drop(columns="vibration")
    elif bad == "empty":
        training = training.iloc[:0]
    elif bad == "duplicate":
        training = pd.concat([training, training[["temp_c"]]], axis=1)
    else:
        training["temp_c"] = training["temp_c"].astype(object)
        training.loc[0, "temp_c"] = {"nan": np.nan, "infinite": np.inf, "text": "bad"}[bad]
    with pytest.raises(ValueError):
        train_model(training)


def test_artifact_round_trip_and_repeatability(training, tmp_path):
    model = train_model(training, n_estimators=30, random_state=7)
    path = tmp_path / "model.joblib"
    save_model(model, path)
    restored = load_model(path)
    assert restored.metadata == model.metadata
    assert restored.metadata["feature_order"] == list(feature_matrix(training).columns)
    assert restored.metadata["training_parameters"]["random_state"] == 7
    assert restored.metadata["training_parameters"]["n_estimators"] == 30
    assert len(restored.metadata["training_sha256"]) == 64
    pd.testing.assert_frame_equal(score_samples(model, training), score_samples(restored, training))
    repeated = train_model(training, n_estimators=30, random_state=7)
    pd.testing.assert_frame_equal(score_samples(model, training), score_samples(repeated, training))
    shuffled = training[["current_ma", "timestamp", "vibration", "temp_c"]]
    assert np.array_equal(
        score_samples(model, training)["score"], score_samples(model, shuffled)["score"]
    )


def test_batch_boundaries_reset_and_failure(training):
    model = train_model(training)
    whole = score_samples(model, training)
    session = InferenceSession(model)
    first = session.score(training.iloc[:17])
    previous = session.previous_temp
    with pytest.raises(ValueError):
        session.score(training.iloc[17:18].drop(columns="temp_c"))
    assert session.previous_temp == previous
    rest = session.score(training.iloc[17:])
    pd.testing.assert_frame_equal(whole, pd.concat([first, rest]))
    session.reset()
    assert session.score(training.iloc[17:])["temp_delta"].iloc[0] == 0
    assert score_samples(model, training.iloc[17:])["temp_delta"].iloc[0] == 0
    assert score_samples(model, training.iloc[:1], previous_temp=23)["temp_delta"].iloc[
        0
    ] == pytest.approx(training.temp_c.iloc[0] - 23)
    with pytest.raises(ValueError):
        score_samples(model, training, previous_temp=np.nan)


def test_held_out_evaluation(training):
    evaluation = pd.read_csv(files("tools").joinpath("data/evaluation.csv"))
    model = train_model(training)
    original = evaluation.copy(deep=True)
    scored, metrics = evaluate_model(model, evaluation)
    assert metrics["true_positives"] == 5
    assert metrics["false_negatives"] == 0
    assert metrics["samples"] == 40
    assert metrics["recall"] == 1
    assert 0 <= metrics["roc_auc"] <= 1
    pd.testing.assert_frame_equal(evaluation, original)
    assert "is_anomaly" in scored
    for labels in ([0] * 40, [None] * 40, [2] * 40):
        with pytest.raises(ValueError):
            evaluate_model(model, evaluation.assign(is_anomaly=labels))


def test_metadata_rejection(training):
    model = train_model(training)
    with pytest.raises(ValueError, match="Legacy"):
        score_samples(model.estimator, training)
    model.metadata["feature_order"].reverse()
    with pytest.raises(ValueError, match="feature order"):
        score_samples(model, training)


def test_installed_pipeline_cli(tmp_path):
    def run(*args):
        return subprocess.run(args, cwd=tmp_path, capture_output=True, text=True, check=True)

    training = str(files("tools").joinpath("data/training.csv"))
    evaluation = str(files("tools").joinpath("data/evaluation.csv"))
    run("embedded-train", "--input", training, "--output", "model.joblib", "--random-state", "7")
    metadata = json.loads((tmp_path / "model.joblib.metadata.json").read_text())
    assert metadata["training_parameters"]["random_state"] == 7
    run(
        "embedded-infer",
        "--model",
        "model.joblib",
        "--input",
        evaluation,
        "--batch-size",
        "7",
        "--output",
        "batch.csv",
    )
    run("embedded-infer", "--model", "model.joblib", "--input", evaluation, "--output", "whole.csv")
    pd.testing.assert_frame_equal(
        pd.read_csv(tmp_path / "batch.csv"), pd.read_csv(tmp_path / "whole.csv")
    )
    run(
        "embedded-evaluate",
        "--model",
        "model.joblib",
        "--input",
        evaluation,
        "--output",
        "scored.csv",
        "--metrics",
        "metrics.json",
    )
    assert json.loads((tmp_path / "metrics.json").read_text())["true_positives"] == 5
    assert len(pd.read_csv(tmp_path / "scored.csv")) == 40
