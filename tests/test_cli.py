"""Exercise installed scripts in a working directory outside the source tree."""

import json
import subprocess

import pytest


def run(*args, cwd):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    "command", ["embedded-device", "embedded-train", "embedded-infer", "embedded-demo"]
)
def test_installed_help(command, tmp_path):
    assert "usage:" in run(command, "--help", cwd=tmp_path).stdout


def test_installed_demo(tmp_path):
    run("embedded-demo", "--output", "result", cwd=tmp_path)
    summary = json.loads((tmp_path / "result/summary.json").read_text())
    assert summary["injected_faults_detected"] == 5
    assert summary["evaluation_samples"] == 40
    assert (tmp_path / "result/predictions.csv").is_file()


def test_training_inference_scripts(tmp_path):
    from importlib.resources import files

    data = str(files("tools").joinpath("data/training.csv"))
    model = str(tmp_path / "model.joblib")
    run("embedded-train", "--input", data, "--output", model, cwd=tmp_path)
    assert (
        "Anomalies detected:"
        in run("embedded-infer", "--input", data, "--model", model, cwd=tmp_path).stdout
    )
