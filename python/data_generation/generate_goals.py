
import csv
import random
from datetime import date, timedelta

import pandas as pd

from python.data_generation.config import (
    DATA_END_DATE,
    RANDOM_SEED,
    RAW_DATA_DIR,
)

random.seed(RANDOM_SEED)

GOAL_TYPES = {
    "WEIGHT_LOSS": ("kg", 3, 20),
    "MUSCLE_GAIN": ("kg", 2, 15),
    "STRENGTH": ("kg", 5, 100),
    "ENDURANCE": ("minutes", 5, 60),
    "FLEXIBILITY": ("cm", 2, 20),
}


def generate_goals():
    members = pd.read_csv(RAW_DATA_DIR / "members.csv")

    end_date = date.fromisoformat(DATA_END_DATE)
    output_file = RAW_DATA_DIR / "member_goals.csv"

    goal_id = 1

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "goal_id",
                "member_id",
                "goal_type",
                "target_value",
                "unit",
                "start_date",
                "target_date",
                "goal_status",
                "created_at",
                "completed_at",
            ],
        )

        writer.writeheader()

        for member in members.itertuples(index=False):
            if random.random() > 0.75:
                continue

            number_of_goals = random.randint(1, 3)

            for _ in range(number_of_goals):
                goal_type = random.choice(list(GOAL_TYPES.keys()))
                unit, minimum, maximum = GOAL_TYPES[goal_type]

                start_date = date.fromisoformat(member.join_date)

                if start_date >= end_date:
                    continue

                goal_start = start_date + timedelta(
                    days=random.randint(
                        0,
                        min(180, (end_date - start_date).days),
                    )
                )

                target_date = goal_start + timedelta(
                    days=random.randint(30, 180)
                )

                completed_at = None

                if target_date <= end_date:
                    status = random.choices(
                        ["COMPLETED", "ABANDONED", "ACTIVE"],
                        weights=[0.45, 0.20, 0.35],
                        k=1,
                    )[0]
                else:
                    target_date = end_date + timedelta(days=30)
                    status = "ACTIVE"

                if status == "COMPLETED":
                    completion_limit = min(target_date, end_date)
                    completion_days = (completion_limit - goal_start).days

                    completed_at = (
                        goal_start
                        + timedelta(days=random.randint(1, completion_days))
                    ).isoformat()

                writer.writerow({
                    "goal_id": goal_id,
                    "member_id": int(member.member_id),
                    "goal_type": goal_type,
                    "target_value": round(
                        random.uniform(minimum, maximum),
                        2,
                    ),
                    "unit": unit,
                    "start_date": goal_start.isoformat(),
                    "target_date": target_date.isoformat(),
                    "goal_status": status,
                    "created_at": goal_start.isoformat(),
                    "completed_at": completed_at,
                })

                goal_id += 1

    print("Member goals generation completed.")
    print(f"Total goals: {goal_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_goals()
