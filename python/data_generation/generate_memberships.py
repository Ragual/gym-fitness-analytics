
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


PLAN_DURATIONS = {
    1: 1,
    2: 3,
    3: 6,
    4: 12,
}

PLAN_WEIGHTS = [0.40, 0.30, 0.20, 0.10]


def generate_memberships():
    members = pd.read_csv(RAW_DATA_DIR / "members.csv")

    end_date = date.fromisoformat(DATA_END_DATE)
    output_file = RAW_DATA_DIR / "memberships.csv"

    membership_id = 1

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "membership_id",
                "member_id",
                "plan_id",
                "start_date",
                "end_date",
                "status",
                "created_at",
            ],
        )

        writer.writeheader()

        for member in members.itertuples(index=False):
            current_start = date.fromisoformat(member.join_date)

            while current_start <= end_date:
                plan_id = random.choices(
                    list(PLAN_DURATIONS.keys()),
                    weights=PLAN_WEIGHTS,
                    k=1,
                )[0]

                duration = PLAN_DURATIONS[plan_id]
                current_end = current_start + timedelta(
                    days=duration * 30 - 1
                )

                if current_end > end_date:
                    status = "ACTIVE"
                else:
                    status = random.choices(
                        ["EXPIRED", "CANCELLED"],
                        weights=[0.85, 0.15],
                        k=1,
                    )[0]

                writer.writerow({
                    "membership_id": membership_id,
                    "member_id": member.member_id,
                    "plan_id": plan_id,
                    "start_date": current_start.isoformat(),
                    "end_date": current_end.isoformat(),
                    "status": status,
                    "created_at": current_start.isoformat(),
                })

                membership_id += 1

                if status == "CANCELLED" or current_end >= end_date:
                    break

                if random.random() > 0.72:
                    break

                current_start = current_end + timedelta(days=1)

    print("Membership generation completed.")
    print(f"Total memberships: {membership_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_memberships()
