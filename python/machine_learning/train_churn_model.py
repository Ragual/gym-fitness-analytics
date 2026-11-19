
import json
from pathlib import Path

import joblib
from opentelemetry import metrics
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "churn_training_dataset.csv"
)
MODEL_DIR = PROJECT_ROOT / "models"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

TARGET = "churned"

TRAIN_SNAPSHOTS = [
    "2026-04-30",
    "2026-05-31",
    "2026-06-30",
    "2026-07-31",
]

VALIDATION_SNAPSHOT = "2026-08-31"
TEST_SNAPSHOT = "2026-09-30"

FEATURES = [
    "attendance_count",
    "active_days",
    "recent_attendance",
    "failed_payments",
    "payment_count",
    "goals_created",
    "goals_completed",
    "workout_sessions",
    "days_since_last_visit",
    "membership_tenure_days",
    "attendance_frequency",
    "attendance_recent_ratio",
    "goal_completion_rate",
]


def create_models():
    return {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            )),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }


def calculate_metrics(model, X, y, threshold=0.5):
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    return {
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
        "positive_rate": float(y.mean()),
        "confusion_matrix": confusion_matrix(
            y, predictions
        ).tolist(),
        "classification_report": classification_report(
            y,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }

def find_best_threshold(model, X, y):
    probabilities = model.predict_proba(X)[:, 1]

    precisions, recalls, thresholds = precision_recall_curve(
        y,
        probabilities,
    )

    f1_scores = (
        2 * precisions[:-1] * recalls[:-1]
        / (precisions[:-1] + recalls[:-1] + 1e-10)
    )

    best_index = f1_scores.argmax()

    return {
        "threshold": float(thresholds[best_index]),
        "precision": float(precisions[best_index]),
        "recall": float(recalls[best_index]),
        "f1_score": float(f1_scores[best_index]),
    }


def train_model():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_FILE}. "
            "Run build_training_dataset first."
        )

    df = pd.read_csv(DATA_FILE)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    required_columns = FEATURES + [
        TARGET,
        "snapshot_date",
        "member_id",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {missing_columns}"
        )

    train_dates = pd.to_datetime(TRAIN_SNAPSHOTS)
    validation_date = pd.Timestamp(VALIDATION_SNAPSHOT)
    test_date = pd.Timestamp(TEST_SNAPSHOT)

    train_df = df[df["snapshot_date"].isin(train_dates)].copy()
    validation_df = df[
        df["snapshot_date"] == validation_date
    ].copy()
    test_df = df[df["snapshot_date"] == test_date].copy()

    if train_df.empty or validation_df.empty or test_df.empty:
        raise ValueError(
            "Training, validation, or test dataset is empty. "
            "Check the available snapshot dates."
        )

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_validation = validation_df[FEATURES]
    y_validation = validation_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    if y_train.nunique() < 2 or y_validation.nunique() < 2:
        raise ValueError(
            "Training and validation data must contain both classes."
        )

    print("\n========== CHRONOLOGICAL CHURN TRAINING ==========")
    print(f"Training rows: {len(train_df):,}")
    print(f"Validation rows: {len(validation_df):,}")
    print(f"Final test rows: {len(test_df):,}")
    print(f"Training snapshots: {TRAIN_SNAPSHOTS}")
    print(f"Validation snapshot: {VALIDATION_SNAPSHOT}")
    print(f"Final test snapshot: {TEST_SNAPSHOT}")

    models = create_models()
    validation_results = {}
    best_model_name = None
    best_validation_score = -1

    # Stage 1: Select the model using August validation data.
    for name, model in models.items():
        print(f"\nTraining candidate: {name}")

        model.fit(X_train, y_train)

        metrics = calculate_metrics(
            model,
            X_validation,
            y_validation,
        )

        validation_results[name] = metrics

        print(f"Validation accuracy: {metrics['accuracy']:.4f}")
        print(f"Validation F1: {metrics['f1_score']:.4f}")
        print(f"Validation PR-AUC: {metrics['pr_auc']:.4f}")
        print(f"Validation positive cases: {metrics['positive_cases']}")
        print(f"Validation ROC-AUC: {metrics['roc_auc']:.4f}")

        if metrics["pr_auc"] > best_validation_score:
            best_validation_score = metrics["pr_auc"]
            best_model_name = name

    # Stage 1B: Select the classification threshold using August validation.
    selected_model = models[best_model_name]

    threshold_results = find_best_threshold(
        selected_model,
        X_validation,
        y_validation,
    )

    best_threshold = threshold_results["threshold"]

    print("\n========== THRESHOLD SELECTION ==========")
    print(f"Selected threshold: {best_threshold:.4f}")
    print(f"Validation precision: {threshold_results['precision']:.4f}")
    print(f"Validation recall: {threshold_results['recall']:.4f}")
    print(f"Validation F1: {threshold_results['f1_score']:.4f}")

    # Stage 2: Refit the selected model using April-August data.
    development_df = df[
        df["snapshot_date"].isin(
            train_dates.tolist() + [validation_date]
        )
    ].copy()

    X_development = development_df[FEATURES]
    y_development = development_df[TARGET]

    final_model = create_models()[best_model_name]
    final_model.fit(X_development, y_development)

    # Stage 3: Evaluate once on the untouched September test data.
    final_test_metrics = calculate_metrics(
        final_model,
        X_test,
        y_test,
        threshold=best_threshold,
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / "churn_model.joblib"
    metrics_path = ARTIFACT_DIR / "churn_metrics.json"

    joblib.dump(
        {
            "model": final_model,
            "model_name": best_model_name,
            "threshold": best_threshold,
            "threshold_metrics": threshold_results,
            "features": FEATURES,
            "training_snapshots": TRAIN_SNAPSHOTS,
            "validation_snapshot": VALIDATION_SNAPSHOT,
            "test_snapshot": TEST_SNAPSHOT,
        },
        model_path,
    )

    results = {
        "evaluation_method": "chronological_snapshot_split",
        "training_snapshots": TRAIN_SNAPSHOTS,
        "validation_snapshot": VALIDATION_SNAPSHOT,
        "test_snapshot": TEST_SNAPSHOT,
        "training_rows": int(len(train_df)),
        "validation_rows": int(len(validation_df)),
        "final_test_rows": int(len(test_df)),
        "validation_results": validation_results,
        "selected_model": best_model_name,
        "final_test_metrics": final_test_metrics,
        "selected_threshold": best_threshold,
        "threshold_validation_metrics": threshold_results,
    }

    with metrics_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("\n========== FINAL TEST RESULTS ==========")
    print(f"Selected model: {best_model_name}")
    print(f"Accuracy:  {final_test_metrics['accuracy']:.4f}")
    print(f"Precision: {final_test_metrics['precision']:.4f}")
    print(f"Recall:    {final_test_metrics['recall']:.4f}")
    print(f"F1 Score:  {final_test_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:   {final_test_metrics['roc_auc']:.4f}")
    print(f"PR-AUC:    {final_test_metrics['pr_auc']:.4f}")
    print(f"Positive cases: {final_test_metrics['positive_cases']}")

    print("\nConfusion matrix:")
    print(final_test_metrics["confusion_matrix"])

    print(f"\nSaved model: {model_path}")
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    train_model()
