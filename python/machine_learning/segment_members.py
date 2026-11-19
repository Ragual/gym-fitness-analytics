
from pathlib import Path

import joblib
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "data" / "processed" / "member_features.csv"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "member_segments.csv"

FEATURES = [
    "attendance_count",
    "active_days",
    "recent_attendance",
    "payment_count",
    "goals_created",
    "goals_completed",
    "workout_sessions",
    "days_since_last_visit",
    "attendance_frequency",
    "goal_completion_rate",
]


def segment_members():
    df = pd.read_csv(DATA_FILE)

    X = df[FEATURES].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
    )

    clusters = model.fit_predict(X_scaled)

    df["segment_id"] = clusters

    silhouette = silhouette_score(X_scaled, clusters)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "scaler": scaler,
            "features": FEATURES,
        },
        MODEL_DIR / "member_segmentation.joblib",
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\n========== MEMBER SEGMENTATION ==========")
    print(f"Members segmented: {len(df)}")
    print(f"Number of clusters: {model.n_clusters}")
    print(f"Silhouette score: {silhouette:.4f}")

    print("\nCluster sizes:")
    print(df["segment_id"].value_counts().sort_index())

    print(f"\nSaved segments: {OUTPUT_FILE}")


if __name__ == "__main__":
    segment_members()
