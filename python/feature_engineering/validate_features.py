
import pandas as pd

from python.data_generation.config import PROCESSED_DATA_DIR


DATASETS = {
    "Latest features": PROCESSED_DATA_DIR / "member_features.csv",
    "Historical training dataset": (
        PROCESSED_DATA_DIR / "churn_training_dataset.csv"
    ),
}


def validate_dataset(name, file_path, historical=False):
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")

    df = pd.read_csv(file_path)

    required_columns = {
        "member_id",
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
        "churned",
    }

    if historical:
        required_columns.add("snapshot_date")

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{name} is missing columns: {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(f"{name} is empty.")

    checks = {
        "Dataset is not empty": len(df) > 0,
        "No missing values": not df.isnull().any().any(),
        "Churn labels are binary": set(
            df["churned"].unique()
        ).issubset({0, 1}),
        "Attendance counts are non-negative": (
            df["attendance_count"] >= 0
        ).all(),
        "Failed payments are non-negative": (
            df["failed_payments"] >= 0
        ).all(),
        "Workout sessions are non-negative": (
            df["workout_sessions"] >= 0
        ).all(),
        "Days since last visit are non-negative": (
            df["days_since_last_visit"] >= 0
        ).all(),
        "Goal completion rate is valid": (
            df["goal_completion_rate"].between(0, 1).all()
        ),
        "Attendance frequency is non-negative": (
            df["attendance_frequency"] >= 0
        ).all(),
    }

    if historical:
        df["snapshot_date"] = pd.to_datetime(
            df["snapshot_date"],
            errors="coerce",
        )

        checks.update({
            "Snapshot dates are valid": (
                df["snapshot_date"].notna().all()
            ),
            "Member-snapshot combinations are unique": (
                not df.duplicated(
                    ["member_id", "snapshot_date"]
                ).any()
            ),
            "Historical dataset has multiple snapshots": (
                df["snapshot_date"].nunique() > 1
            ),
        })
    else:
        checks["Member IDs are unique"] = (
            df["member_id"].is_unique
        )

    print(f"\n========== {name.upper()} ==========\n")

    failed = 0

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check_name}")

        if not passed:
            failed += 1

    print("\n========== SUMMARY ==========\n")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print(f"Unique members: {df['member_id'].nunique():,}")
    print(f"Churn rate: {df['churned'].mean():.2%}")

    if historical:
        print(f"Snapshots: {df['snapshot_date'].nunique()}")

    print(f"Checks: {len(checks)}")
    print(f"Failed: {failed}")

    if failed:
        raise ValueError(f"{name} validation failed.")


def validate_features():
    for name, file_path in DATASETS.items():
        validate_dataset(
            name,
            file_path,
            historical=(name == "Historical training dataset"),
        )

    print("\nAll feature datasets passed validation.")


if __name__ == "__main__":
    validate_features()
