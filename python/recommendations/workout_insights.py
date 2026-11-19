
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURES_FILE = PROJECT_ROOT / "data" / "processed" / "member_features.csv"
SEGMENTS_FILE = PROJECT_ROOT / "data" / "processed" / "member_segments.csv"
RECOMMENDATIONS_FILE = (
    PROJECT_ROOT / "data" / "processed" / "workout_recommendations.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "workout_insights.json"


def generate_insights():
    features = pd.read_csv(FEATURES_FILE)
    segments = pd.read_csv(SEGMENTS_FILE)
    recommendations = pd.read_csv(RECOMMENDATIONS_FILE)

    insights = {
        "total_members": int(len(features)),
        "average_attendance": round(
            float(features["attendance_count"].mean()), 2
        ),
        "average_workout_sessions": round(
            float(features["workout_sessions"].mean()), 2
        ),
        "overall_churn_rate": round(
            float(features["churned"].mean() * 100), 2
        ),
        "segment_sizes": {
            str(int(key)): int(value)
            for key, value in segments["segment_id"]
            .value_counts().sort_index().items()
        },
        "recommendation_distribution": {
            str(key): int(value)
            for key, value in recommendations[
                "recommendation_type"
            ].value_counts().items()
        },
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    import json

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(insights, file, indent=4)

    print("\n========== WORKOUT INSIGHTS ==========")

    for key, value in insights.items():
        print(f"{key}: {value}")

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_insights()
