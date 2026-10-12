"""Evaluate an independent, labeled telemetry recording without fitting on it."""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, roc_auc_score

from ml.model import load_model, score_samples


def evaluate_model(model, dataframe, *, label_column="is_anomaly"):
    if label_column not in dataframe:
        raise ValueError(f"Missing evaluation label column: {label_column}")
    labels = dataframe[label_column]
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("Evaluation labels must be nonmissing binary 0/1 values")
    if labels.nunique() != 2:
        raise ValueError("Evaluation requires both normal and anomalous samples")
    scored = score_samples(model, dataframe)
    predictions = (scored["anomaly"] == "ANOMALY").astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="binary", zero_division=0
    )
    metrics = {
        "samples": len(scored),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc_score(labels, -scored["score"])),
    }
    return scored, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--label-column", default="is_anomaly")
    parser.add_argument("--output", default="evaluation-scored.csv")
    parser.add_argument("--metrics", default="evaluation-metrics.json")
    args = parser.parse_args()
    scored, metrics = evaluate_model(
        load_model(args.model), pd.read_csv(args.input), label_column=args.label_column
    )
    scored.to_csv(args.output, index=False)
    Path(args.metrics).write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
