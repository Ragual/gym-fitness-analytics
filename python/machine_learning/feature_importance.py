
from pathlib import Path

import joblib
import pandas as pd

from sklearn.inspection import permutation_importance


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "churn_training_dataset.csv"
)
MODEL_FILE = PROJECT_ROOT / "models" / "churn_model.joblib"
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "feature_importance.csv"


def calculate_feature_importance():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

    df = pd.read_csv(DATA_FILE)
    saved_model = joblib.load(MODEL_FILE)

    model = saved_model["model"]
    features = saved_model["features"]
    test_snapshot = saved_model["test_snapshot"]

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
            "Feature importance requires both classes in test data."
        )

    results = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=20,
        random_state=42,
        scoring="average_precision",
        n_jobs=-1,
    )

    importance_df = pd.DataFrame({
        "feature": features,
        "importance_mean": results.importances_mean,
        "importance_std": results.importances_std,
    })

    importance_df = importance_df.sort_values(
        by="importance_mean",
        ascending=False,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(OUTPUT_FILE, index=False)

    print("\n========== FEATURE IMPORTANCE ==========")
    print(f"Evaluation snapshot: {test_snapshot}")
    print("Scoring metric: Average Precision (PR-AUC)")
    print(importance_df.to_string(index=False))
    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    calculate_feature_importance()
