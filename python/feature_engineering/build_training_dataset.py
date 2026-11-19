
import pandas as pd

from python.feature_engineering.build_features import (
    build_features_for_snapshot,
)
from python.data_generation.config import PROCESSED_DATA_DIR


SNAPSHOT_DATES = [
    "2026-04-30",
    "2026-05-31",
    "2026-06-30",
    "2026-07-31",
    "2026-08-31",
    "2026-09-30",
]


def build_training_dataset():
    snapshots = []

    print("\n========== HISTORICAL DATASET BUILD ==========")

    for snapshot_date in SNAPSHOT_DATES:
        print(f"\nBuilding snapshot: {snapshot_date}")

        features = build_features_for_snapshot(snapshot_date)

        snapshots.append(features)

        print(f"Members: {len(features):,}")
        print(f"Churn rate: {features['churned'].mean():.2%}")

    dataset = pd.concat(
        snapshots,
        ignore_index=True,
    )

    dataset["snapshot_date"] = pd.to_datetime(
        dataset["snapshot_date"]
    )

    dataset = dataset.sort_values(
        ["snapshot_date", "member_id"]
    ).reset_index(drop=True)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        PROCESSED_DATA_DIR / "churn_training_dataset.csv"
    )

    dataset.to_csv(output_file, index=False)

    print("\n========== DATASET SUMMARY ==========")
    print(f"Total rows: {len(dataset):,}")
    print(f"Unique members: {dataset['member_id'].nunique():,}")
    print(f"Snapshots: {dataset['snapshot_date'].nunique()}")
    print(f"Overall churn rate: {dataset['churned'].mean():.2%}")

    print("\nRows by snapshot:")
    print(
        dataset.groupby("snapshot_date")
        .agg(
            members=("member_id", "count"),
            churn_rate=("churned", "mean"),
        )
        .to_string()
    )

    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    build_training_dataset()
