
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PIPELINE_STEPS = [
    (
        "Member generation",
        "python.data_generation.generate_members",
    ),
    (
        "Membership generation",
        "python.data_generation.generate_memberships",
    ),
    (
        "Attendance generation",
        "python.data_generation.generate_attendance",
    ),
    (
        "Payment generation",
        "python.data_generation.generate_payments",
    ),
    (
        "Goal generation",
        "python.data_generation.generate_goals",
    ),
    (
        "Workout generation",
        "python.data_generation.generate_workouts",
    ),
    (
        "Workout log generation",
        "python.data_generation.generate_workout_logs",
    ),
    (
        "Data validation",
        "python.data_generation.validate_data",
    ),
    (
        "Database loading",
        "python.pipelines.load_data",
    ),
    (
        "Database quality checks",
        "python.pipelines.data_quality",
    ),
    (
        "Feature engineering",
        "python.feature_engineering.build_features",
    ),
    (
        "Historical training dataset generation",
        "python.feature_engineering.build_training_dataset",
    ),
    (
        "Feature validation",
        "python.feature_engineering.validate_features",
    ),
    (
        "Churn model training",
        "python.machine_learning.train_churn_model",
    ),
    (
        "Model evaluation",
        "python.machine_learning.evaluate_model",
    ),
    (
        "Feature importance",
        "python.machine_learning.feature_importance",
    ),
    (
        "Model monitoring",
        "python.machine_learning.monitor_model",
    ),
    (
        "Member segmentation",
        "python.machine_learning.segment_members",
    ),
    (
        "Segment profiling",
        "python.machine_learning.profile_segments",
    ),
    (
        "Workout recommendations",
        "python.recommendations.workout_recommender",
    ),
    (
        "Workout insights",
        "python.recommendations.workout_insights",
    ),
]


def run_step(name, module):
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {name}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline failed at step: {name}"
        )

    print(f"\nCOMPLETED: {name}")


def main():
    print("\nAI GYM INTELLIGENCE PLATFORM")
    print("AUTOMATED ETL AND ML PIPELINE")

    for name, module in PIPELINE_STEPS:
        run_step(name, module)

    print("\n" + "=" * 60)
    print("ALL PIPELINE STEPS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
