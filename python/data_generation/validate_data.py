
import pandas as pd

from python.data_generation.config import RAW_DATA_DIR

FILES = {
    "members": "members.csv",
    "memberships": "memberships.csv",
    "attendance": "attendance.csv",
    "payments": "payments.csv",
    "member_goals": "member_goals.csv",
    "workout_sessions": "workout_sessions.csv",
    "workout_logs": "workout_logs.csv",
}

def validate():
    datasets = {}

    print("\n========== DATASET VALIDATION ==========\n")

    for name, filename in FILES.items():
        path = RAW_DATA_DIR / filename
        df = pd.read_csv(path)
        datasets[name] = df

        print(f"{name}:")
        print(f"  Rows: {len(df):,}")
        print(f"  Missing values: {df.isnull().sum().sum():,}")
        print(f"  Duplicate rows: {df.duplicated().sum():,}")

    checks = {
        "Membership -> Member": (
            datasets["memberships"]["member_id"],
            datasets["members"]["member_id"],
        ),
        "Attendance -> Member": (
            datasets["attendance"]["member_id"],
            datasets["members"]["member_id"],
        ),
        "Payments -> Membership": (
            datasets["payments"]["membership_id"],
            datasets["memberships"]["membership_id"],
        ),
        "Goals -> Member": (
            datasets["member_goals"]["member_id"],
            datasets["members"]["member_id"],
        ),
        "Sessions -> Member": (
            datasets["workout_sessions"]["member_id"],
            datasets["members"]["member_id"],
        ),
        "Sessions -> Trainer": (
            datasets["workout_sessions"]["trainer_id"].dropna().astype(int),
            pd.Series([1, 2, 3, 4, 5]),
        ),
        "Workout logs -> Session": (
            datasets["workout_logs"]["session_id"],
            datasets["workout_sessions"]["session_id"],
        ),
        "Workout logs -> Exercise": (
            datasets["workout_logs"]["exercise_id"],
            pd.Series(range(1, 11)),
        ),
    }

    print("\n========== FOREIGN KEY VALIDATION ==========\n")

    for name, (child, parent) in checks.items():
        invalid = (~child.isin(parent)).sum()
        status = "PASS" if invalid == 0 else "FAIL"
        print(f"{status}: {name} | Invalid references: {invalid:,}")

    print("\n========== PRIMARY KEY VALIDATION ==========\n")

    primary_keys = {
        "members": "member_id",
        "memberships": "membership_id",
        "attendance": "attendance_id",
        "payments": "payment_id",
        "member_goals": "goal_id",
        "workout_sessions": "session_id",
        "workout_logs": "workout_id",
    }

    for name, key in primary_keys.items():
        duplicates = datasets[name][key].duplicated().sum()
        status = "PASS" if duplicates == 0 else "FAIL"
        print(f"{status}: {name}.{key} | Duplicates: {duplicates:,}")


if __name__ == "__main__":
    validate()
