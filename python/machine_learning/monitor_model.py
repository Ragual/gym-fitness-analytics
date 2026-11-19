
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "churn_training_dataset.csv"
)
MODEL_FILE = PROJECT_ROOT / "models" / "churn_model.joblib"
METRICS_FILE = PROJECT_ROOT / "artifacts" / "churn_metrics.json"
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "model_monitoring.json"


def monitor_model():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

    if not METRICS_FILE.exists():
        raise FileNotFoundError(f"Baseline metrics not found: {METRICS_FILE}")

    df = pd.read_csv(DATA_FILE)
    saved_model = joblib.load(MODEL_FILE)

    model = saved_model["model"]
    features = saved_model["features"]
    test_snapshot = saved_model["test_snapshot"]
    threshold = float(saved_model.get("threshold", 0.5))

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    test_df = df[
        df["snapshot_date"] == pd.Timestamp(test_snapshot)
    ].copy()

    if test_df.empty:
        raise ValueError(
            f"No test data found for snapshot {test_snapshot}."
        )

    X = test_df[features]
    y = test_df["churned"]

    if y.nunique() < 2:
        raise ValueError(
            "Monitoring requires both churn classes in the test data."
        )

    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    current_metrics = {
        "accuracy": float(accuracy_score(y, predictions)),
        "precision": float(precision_score(
            y, predictions, zero_division=0
        )),
        "recall": float(recall_score(
            y, predictions, zero_division=0
        )),
        "f1_score": float(f1_score(
            y, predictions, zero_division=0
        )),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "pr_auc": float(average_precision_score(y, probabilities)),
        "positive_cases": int(y.sum()),
        "confusion_matrix": confusion_matrix(
            y, predictions
        ).tolist(),
    }

    with METRICS_FILE.open("r", encoding="utf-8") as file:
        baseline_metrics = json.load(file)

    baseline = baseline_metrics["final_test_metrics"]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_name": saved_model["model_name"],
        "evaluation_scope": "September chronological holdout",
        "test_snapshot": test_snapshot,
        "test_rows": int(len(test_df)),
        "decision_threshold": threshold,
        "baseline_metrics": {
            "accuracy": baseline["accuracy"],
            "precision": baseline["precision"],
            "recall": baseline["recall"],
            "f1_score": baseline["f1_score"],
            "roc_auc": baseline["roc_auc"],
            "pr_auc": baseline["pr_auc"],
        },
        "current_metrics": current_metrics,
        "notes": (
            "This report rechecks the saved final holdout using "
            "the saved decision threshold. It is a reproducibility "
            "diagnostic, not ongoing production monitoring or "
            "evidence of model drift. The evaluation uses synthetic "
            "data and a small number of positive cases."
        ),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n========== MODEL MONITORING ==========")
    print(f"Model: {saved_model['model_name']}")
    print(f"Evaluation snapshot: {test_snapshot}")
    print(f"Test rows: {len(test_df):,}")
    print(f"Decision threshold: {threshold:.4f}")
    print(f"Accuracy:  {current_metrics['accuracy']:.4f}")
    print(f"Precision: {current_metrics['precision']:.4f}")
    print(f"Recall:    {current_metrics['recall']:.4f}")
    print(f"F1 Score:  {current_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:   {current_metrics['roc_auc']:.4f}")
    print(f"PR-AUC:    {current_metrics['pr_auc']:.4f}")
    print(f"Report saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    monitor_model()
