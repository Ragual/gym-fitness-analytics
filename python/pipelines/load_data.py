
import csv

from python.database import get_connection
from python.data_generation.config import RAW_DATA_DIR


DATASETS = [
    {
        "file": "members.csv",
        "table": "members",
        "columns": [
            "member_id", "full_name", "email", "date_of_birth",
            "gender", "join_date", "created_at",
        ],
    },
    {
        "file": "memberships.csv",
        "table": "memberships",
        "columns": [
            "membership_id", "member_id", "plan_id", "start_date",
            "end_date", "status", "created_at",
        ],
    },
    {
        "file": "attendance.csv",
        "table": "attendance",
        "columns": [
            "attendance_id", "member_id", "check_in", "check_out",
            "created_at",
        ],
    },
    {
        "file": "payments.csv",
        "table": "payments",
        "columns": [
            "payment_id", "membership_id", "amount", "payment_date",
            "payment_method", "payment_status", "transaction_reference",
            "created_at",
        ],
    },
    {
        "file": "member_goals.csv",
        "table": "member_goals",
        "columns": [
            "goal_id", "member_id", "goal_type", "target_value", "unit",
            "start_date", "target_date", "goal_status", "created_at",
            "completed_at",
        ],
    },
    {
        "file": "workout_sessions.csv",
        "table": "workout_sessions",
        "columns": [
            "session_id", "member_id", "trainer_id", "session_date",
            "duration_minutes", "notes",
        ],
    },
    {
        "file": "workout_logs.csv",
        "table": "workout_logs",
        "columns": [
            "workout_id", "session_id", "exercise_id", "sets", "reps",
            "weight_kg", "created_at",
        ],
    },
]


def load_dataset(cursor, dataset):
    file_path = RAW_DATA_DIR / dataset["file"]
    columns = dataset["columns"]
    table = dataset["table"]

    column_names = ", ".join(columns)

    copy_sql = (
        f"COPY {table} ({column_names}) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )

    with file_path.open("rb") as file:
        with cursor.copy(copy_sql) as copy:
            while chunk := file.read(1024 * 1024):
                copy.write(chunk)

    print(f"Loaded {table}")


def reset_identity_sequences(cursor):
    tables = [
        ("members", "member_id"),
        ("memberships", "membership_id"),
        ("attendance", "attendance_id"),
        ("payments", "payment_id"),
        ("member_goals", "goal_id"),
        ("workout_sessions", "session_id"),
        ("workout_logs", "workout_id"),
    ]

    for table, column in tables:
        cursor.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence(%s, %s),
                COALESCE((SELECT MAX({column}) FROM {table}), 1),
                EXISTS (SELECT 1 FROM {table})
            );
            """,
            (table, column),
        )


def load_all_data():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Clear existing generated records in dependency order.
            cursor.execute("""
                TRUNCATE TABLE
                    workout_logs,
                    workout_sessions,
                    member_goals,
                    payments,
                    attendance,
                    memberships,
                    members
                RESTART IDENTITY CASCADE;
            """)

            for dataset in DATASETS:
                load_dataset(cursor, dataset)

            reset_identity_sequences(cursor)

        connection.commit()

    print("\nAll datasets loaded successfully.")


if __name__ == "__main__":
    load_all_data()
