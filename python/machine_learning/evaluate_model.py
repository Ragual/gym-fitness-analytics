
import json
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
    classification_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "churn_training_dataset.csv"
)
MODEL_FILE = PROJECT_ROOT / "models" / "churn_model.joblib"
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "model_evaluation.json"


def evaluate_model():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

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

    X_test = test_df[features]
    y_test = test_df["churned"]

    if y_test.nunique() < 2:
        raise ValueError(
            "Final test data must contain both churn classes."
        )

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    metrics = {
        "evaluation_method": "chronological_holdout",
        "model_name": saved_model["model_name"],
        "test_snapshot": test_snapshot,
        "test_rows": int(len(test_df)),
        "decision_threshold": threshold,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(
            y_test, predictions, zero_division=0
        )),
        "recall": float(recall_score(
            y_test, predictions, zero_division=0
        )),
        "f1_score": float(f1_score(
            y_test, predictions, zero_division=0
        )),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "pr_auc": float(average_precision_score(y_test, probabilities)),
        "positive_cases": int(y_test.sum()),
        "confusion_matrix": confusion_matrix(
            y_test, predictions
        ).tolist(),
        "classification_report": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print("\n========== CHRONOLOGICAL MODEL EVALUATION ==========")
    print(f"Model: {saved_model['model_name']}")
    print(f"Test snapshot: {test_snapshot}")
    print(f"Test rows: {len(test_df):,}")
    print(f"Decision threshold: {threshold:.4f}")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1_score']:.4f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"PR-AUC:    {metrics['pr_auc']:.4f}")

    print("\nConfusion matrix:")
    print(metrics["confusion_matrix"])

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0,
    ))

    print(f"\nEvaluation saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    evaluate_model()
