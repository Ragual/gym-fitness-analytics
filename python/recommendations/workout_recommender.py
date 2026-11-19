
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "data" / "processed" / "member_features.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "workout_recommendations.csv"


def recommend_workouts():
    df = pd.read_csv(DATA_FILE)

    recommendations = []

    for _, member in df.iterrows():
        attendance = member["attendance_frequency"]
        days_since_visit = member["days_since_last_visit"]
        workout_sessions = member["workout_sessions"]
        goal_rate = member["goal_completion_rate"]

        if days_since_visit >= 21:
            recommendation = (
                "Re-engagement workout",
                "Begin with a light full-body session"
            )

        elif attendance < 0.10:
            recommendation = (
                "Beginner consistency plan",
                "Schedule two beginner sessions per week"
            )

        elif goal_rate < 0.30:
            recommendation = (
                "Goal-focused training",
                "Use measurable weekly workout targets"
            )

        elif workout_sessions >= 30:
            recommendation = (
                "Progressive overload plan",
                "Review training loads and gradually increase intensity"
            )

        else:
            recommendation = (
                "Balanced fitness plan",
                "Combine strength and cardiovascular training"
            )

        recommendations.append({
            "member_id": member["member_id"],
            "recommendation_type": recommendation[0],
            "recommendation": recommendation[1],
        })

    result = pd.DataFrame(recommendations)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("\n========== WORKOUT RECOMMENDATIONS ==========")
    print(f"Members processed: {len(result)}")

    print("\nRecommendation distribution:")
    print(result["recommendation_type"].value_counts())

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    recommend_workouts()
