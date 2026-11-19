
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "member_segments.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "segment_profiles.csv"
)


def profile_segments():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Segment dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    profile = (
        df.groupby("segment_id")
        .agg(
            member_count=("member_id", "count"),
            avg_attendance=("attendance_count", "mean"),
            avg_active_days=("active_days", "mean"),
            avg_recent_attendance=("recent_attendance", "mean"),
            avg_days_since_visit=("days_since_last_visit", "mean"),
            avg_payment_count=("payment_count", "mean"),
            avg_workout_sessions=("workout_sessions", "mean"),
            avg_goal_completion_rate=("goal_completion_rate", "mean"),
            churn_rate=("churned", "mean"),
        )
        .reset_index()
    )

    profile["churn_rate"] = profile["churn_rate"] * 100

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    profile.to_csv(OUTPUT_FILE, index=False)

    print("\n========== MEMBER SEGMENT PROFILES ==========")
    print(profile.round(2).to_string(index=False))
    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    profile_segments()
