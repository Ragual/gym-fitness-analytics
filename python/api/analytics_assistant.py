
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"


def load_dataset(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def load_member_data():
    return load_dataset("member_features.csv")


def load_segment_data():
    return load_dataset("member_segments.csv")


def load_recommendations():
    return load_dataset("workout_recommendations.csv")


def answer_question(question: str) -> dict:
    question = question.lower().strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "source": "input_validation",
        }

    members = load_member_data()
    segments = load_segment_data()
    recommendations = load_recommendations()

    if members.empty:
        return {
            "answer": "Member analytics data is unavailable. Run the data pipeline first.",
            "source": "data_validation",
        }

    # Member segmentation
    if any(term in question for term in [
        "segment",
        "cluster",
        "group of members",
        "member groups",
    ]):
        if segments.empty:
            return {
                "answer": "Member segmentation data is unavailable.",
                "source": "member_segments",
            }

        segment_column = next(
            (
                column
                for column in ["segment", "cluster", "segment_id"]
                if column in segments.columns
            ),
            None,
        )

        if segment_column is None:
            return {
                "answer": "A segment identifier was not found.",
                "source": "member_segments",
            }

        counts = segments[segment_column].value_counts().sort_index()

        summary = ", ".join(
            f"Segment {segment}: {count:,} members"
            for segment, count in counts.items()
        )

        return {
            "answer": (
                f"The analytics cohort contains {len(segments):,} segmented "
                f"members across {len(counts)} groups. {summary}."
            ),
            "source": "member_segments",
        }

    # Churn / inactivity risk
    if any(term in question for term in [
        "churn",
        "leaving",
        "leave",
        "at risk",
    ]):
        if "churned" not in members.columns:
            return {
                "answer": "Inactivity-risk labels are unavailable.",
                "source": "member_features",
            }

        churned = int(members["churned"].sum())
        total = len(members)
        rate = churned / total * 100 if total else 0

        return {
            "answer": (
                f"{churned:,} out of {total:,} eligible members had no "
                f"recorded visits during the 30-day prediction window. "
                f"This represents a {rate:.2f}% 30-day inactivity-risk "
                f"label rate."
            ),
            "source": "member_features",
        }

    # Total registered members
    if any(term in question for term in [
        "total members",
        "how many members",
        "number of members",
        "member count",
        "registered members",
    ]):
        return {
            "answer": (
                f"The analytics cohort contains {len(members):,} eligible "
                "members. The database contains 2,000 generated member "
                "records."
            ),
            "source": "member_features",
        }

    # Attendance
    if "attendance" in question or "visits" in question:
        if "attendance_count" not in members.columns:
            return {
                "answer": "Attendance information is unavailable.",
                "source": "member_features",
            }

        average = members["attendance_count"].mean()
        highest = int(members["attendance_count"].max())

        return {
            "answer": (
                f"Average attendance is {average:.2f} visits per eligible "
                f"member. The highest recorded attendance is {highest}."
            ),
            "source": "member_features",
        }

    # Inactive members
    if any(term in question for term in [
        "inactive",
        "not visited",
        "haven't visited",
        "havent visited",
        "no recent visit",
    ]):
        if "days_since_last_visit" not in members.columns:
            return {
                "answer": "Visit history is unavailable.",
                "source": "member_features",
            }

        inactive = members[members["days_since_last_visit"] >= 30]

        return {
            "answer": (
                f"{len(inactive):,} eligible members have not visited in "
                "at least 30 days, based on the feature snapshot."
            ),
            "source": "member_features",
        }

    # Payment failures
    if "payment" in question or "failed transaction" in question:
        if "failed_payments" not in members.columns:
            return {
                "answer": "Payment information is unavailable.",
                "source": "member_features",
            }

        affected = int((members["failed_payments"] > 0).sum())
        failures = int(members["failed_payments"].sum())

        return {
            "answer": (
                f"{affected:,} members have at least one recorded failed "
                f"payment. Total failed payments: {failures:,}."
            ),
            "source": "member_features",
        }

    # Workout recommendations
    if any(term in question for term in [
        "workout",
        "recommendation",
        "training plan",
    ]):
        if recommendations.empty:
            return {
                "answer": "Workout recommendation data is unavailable.",
                "source": "workout_recommendations",
            }

        column = next(
            (
                name
                for name in [
                    "recommendation_type",
                    "recommendation",
                    "recommended_workout",
                    "workout_recommendation",
                ]
                if name in recommendations.columns
            ),
            None,
        )

        if column is None:
            return {
                "answer": "The recommendation category was not found.",
                "source": "workout_recommendations",
            }

        counts = recommendations[column].value_counts()

        if counts.empty:
            answer = "No workout recommendations are available."
        else:
            answer = "Workout recommendation distribution: " + ", ".join(
                f"{name}: {count:,}"
                for name, count in counts.items()
            ) + "."

        return {
            "answer": answer,
            "source": "workout_recommendations",
        }

    # Goal completion
    if "goal" in question:
        required = {"goals_created", "goals_completed"}

        if not required.issubset(members.columns):
            return {
                "answer": "Member goal information is unavailable.",
                "source": "member_features",
            }

        created = int(members["goals_created"].sum())
        completed = int(members["goals_completed"].sum())
        rate = completed / created * 100 if created else 0

        return {
            "answer": (
                f"The eligible cohort has {created:,} recorded goals and "
                f"{completed:,} completed goals. The overall goal "
                f"completion rate is {rate:.2f}%."
            ),
            "source": "member_features",
        }

    return {
        "answer": (
            "I couldn't identify that analytics request. Try asking about "
            "members, churn, attendance, inactive members, payments, "
            "segments, workout recommendations or goals."
        ),
        "source": "fallback",
    }
