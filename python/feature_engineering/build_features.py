
import pandas as pd

from python.database import get_connection
from python.data_generation.config import (
    SNAPSHOT_DATE,
    FEATURE_WINDOW_DAYS,
    CHURN_PREDICTION_WINDOW_DAYS,
    PROCESSED_DATA_DIR,
)


def build_features_for_snapshot(snapshot_date):
    snapshot = pd.Timestamp(snapshot_date).normalize()

    # Exactly FEATURE_WINDOW_DAYS calendar days, including snapshot date.
    feature_start = snapshot - pd.Timedelta(
        days=FEATURE_WINDOW_DAYS - 1
    )

    label_end = snapshot + pd.Timedelta(
        days=CHURN_PREDICTION_WINDOW_DAYS
    )

    query = """
        WITH attendance_features AS (
            SELECT
                member_id,
                COUNT(*) AS attendance_count,
                COUNT(DISTINCT DATE(check_in)) AS active_days,
                MAX(check_in) AS last_visit,
                COUNT(*) FILTER (
                    WHERE check_in >= %s
                ) AS recent_attendance
            FROM attendance
            WHERE check_in >= %s
              AND check_in < %s
            GROUP BY member_id
        ),

        payment_features AS (
            SELECT
                ms.member_id,
                COUNT(*) FILTER (
                    WHERE p.payment_status = 'FAILED'
                ) AS failed_payments,
                COUNT(p.payment_id) AS payment_count
            FROM memberships ms
            LEFT JOIN payments p
                ON p.membership_id = ms.membership_id
               AND p.payment_date >= %s
               AND p.payment_date < %s
            WHERE ms.start_date <= %s
            GROUP BY ms.member_id
        ),

        goal_features AS (
            SELECT
                member_id,
                COUNT(*) AS goals_created,
                COUNT(*) FILTER (
                    WHERE completed_at IS NOT NULL
                      AND completed_at <= %s
                ) AS goals_completed
            FROM member_goals
            WHERE start_date <= %s
            GROUP BY member_id
        ),

        workout_features AS (
            SELECT
                member_id,
                COUNT(*) AS workout_sessions
            FROM workout_sessions
            WHERE session_date >= %s
              AND session_date < %s
            GROUP BY member_id
        ),

        membership_features AS (
            SELECT
                member_id,
                MAX(end_date) AS latest_membership_end
            FROM memberships
            WHERE start_date <= %s
            GROUP BY member_id
        ),

        future_activity AS (
            SELECT
                member_id,
                COUNT(*) AS future_visits
            FROM attendance
            WHERE check_in >= %s
              AND check_in < %s
            GROUP BY member_id
        )

        SELECT
            m.member_id,
            m.join_date,

            COALESCE(a.attendance_count, 0) AS attendance_count,
            COALESCE(a.active_days, 0) AS active_days,
            a.last_visit,
            COALESCE(a.recent_attendance, 0) AS recent_attendance,

            COALESCE(p.failed_payments, 0) AS failed_payments,
            COALESCE(p.payment_count, 0) AS payment_count,

            COALESCE(g.goals_created, 0) AS goals_created,
            COALESCE(g.goals_completed, 0) AS goals_completed,

            COALESCE(w.workout_sessions, 0) AS workout_sessions,

            mf.latest_membership_end,

            COALESCE(f.future_visits, 0) AS future_visits

        FROM members m

        LEFT JOIN attendance_features a
            ON a.member_id = m.member_id

        LEFT JOIN payment_features p
            ON p.member_id = m.member_id

        LEFT JOIN goal_features g
            ON g.member_id = m.member_id

        LEFT JOIN workout_features w
            ON w.member_id = m.member_id

        LEFT JOIN membership_features mf
            ON mf.member_id = m.member_id

        LEFT JOIN future_activity f
            ON f.member_id = m.member_id

        WHERE m.join_date <= %s
            AND mf.latest_membership_end > %s

        ORDER BY m.member_id;
    """

    params = (
        snapshot - pd.Timedelta(days=44),
        feature_start,
        snapshot + pd.Timedelta(days=1),

        feature_start,
        snapshot + pd.Timedelta(days=1),
        snapshot,

        snapshot,
        snapshot,

        feature_start,
        snapshot + pd.Timedelta(days=1),

        snapshot,

        snapshot + pd.Timedelta(days=1),
        label_end + pd.Timedelta(days=1),

        snapshot,
        label_end,
    )

    with get_connection() as connection:
        features = pd.read_sql_query(
            query,
            connection,
            params=params,
        )

    if features.empty:
        raise ValueError(
            f"No eligible members found for snapshot {snapshot.date()}."
        )

    features["join_date"] = pd.to_datetime(features["join_date"])
    features["last_visit"] = pd.to_datetime(features["last_visit"])
    features["latest_membership_end"] = pd.to_datetime(
        features["latest_membership_end"]
    )

    features["snapshot_date"] = snapshot.date()

    features["days_since_last_visit"] = (
        snapshot - features["last_visit"]
    ).dt.days

    features["days_since_last_visit"] = (
        features["days_since_last_visit"]
        .fillna(FEATURE_WINDOW_DAYS + 1)
        .clip(lower=0)
    )

    features["membership_tenure_days"] = (
        snapshot - features["join_date"]
    ).dt.days.clip(lower=0)

    features["attendance_frequency"] = (
        features["attendance_count"] / FEATURE_WINDOW_DAYS
    )

    features["attendance_recent_ratio"] = (
        features["recent_attendance"]
        / features["attendance_count"].replace(0, 1)
    )

    features["goal_completion_rate"] = (
        features["goals_completed"]
        / features["goals_created"].replace(0, 1)
    )

    features["churned"] = (
        features["future_visits"] == 0
    ).astype(int)

    features = features.drop(
        columns=[
            "join_date",
            "last_visit",
            "latest_membership_end",
            "future_visits",
        ]
    )

    return features


def build_features():
    features = build_features_for_snapshot(SNAPSHOT_DATE)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DATA_DIR / "member_features.csv"
    features.to_csv(output_file, index=False)

    print("\n========== FEATURE ENGINEERING ==========")
    print(f"Snapshot: {SNAPSHOT_DATE}")
    print(f"Members: {len(features):,}")
    print(f"Features: {len(features.columns) - 2}")
    print(f"Churned: {features['churned'].sum():,}")
    print(
        f"Not churned: {(features['churned'] == 0).sum():,}"
    )
    print(
        f"Churn rate: {features['churned'].mean():.2%}"
    )
    print(f"Output: {output_file}")


if __name__ == "__main__":
    build_features()
