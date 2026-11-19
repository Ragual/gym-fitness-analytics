
import csv
import random
from datetime import date, datetime, time, timedelta

import pandas as pd

from python.data_generation.config import (
    DATA_END_DATE,
    RANDOM_SEED,
    RAW_DATA_DIR,
)

random.seed(RANDOM_SEED)


def generate_attendance():
    memberships = pd.read_csv(RAW_DATA_DIR / "memberships.csv")

    end_date = date.fromisoformat(DATA_END_DATE)
    output_file = RAW_DATA_DIR / "attendance.csv"

    attendance_id = 1

    # Behaviour profiles influence attendance frequency.
    profiles = {
        "consistent": (0.80, 0.95),
        "occasional": (0.35, 0.55),
        "declining": (0.70, 0.15),
        "inactive": (0.05, 0.05),
        "loyal": (0.90, 0.98),
    }

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "attendance_id",
                "member_id",
                "check_in",
                "check_out",
                "created_at",
            ],
        )
        writer.writeheader()

        for member_id, group in memberships.groupby("member_id"):
            profile = random.choices(
                list(profiles.keys()),
                weights=[0.30, 0.30, 0.18, 0.12, 0.10],
                k=1,
            )[0]

            early_rate, late_rate = profiles[profile]

            for membership in group.itertuples(index=False):
                start = date.fromisoformat(membership.start_date)
                finish = min(
                    date.fromisoformat(membership.end_date),
                    end_date,
                )

                if finish < start:
                    continue

                current_day = start

                while current_day <= finish:
                    days_elapsed = (current_day - start).days
                    progress = days_elapsed / max((finish - start).days, 1)

                    if profile == "declining":
                        attendance_rate = (
                            early_rate * (1 - progress)
                            + late_rate * progress
                        )
                    else:
                        attendance_rate = early_rate

                    if random.random() < attendance_rate:
                        # 2–5 possible visits per week, spread across days.
                        if random.random() < 0.65:
                            check_in_time = time(
                                hour=random.randint(5, 20),
                                minute=random.choice([0, 15, 30, 45]),
                            )

                            check_in = datetime.combine(
                                current_day,
                                check_in_time,
                            )

                            duration = random.randint(30, 120)
                            check_out = check_in + timedelta(
                                minutes=duration
                            )

                            writer.writerow({
                                "attendance_id": attendance_id,
                                "member_id": int(member_id),
                                "check_in": check_in.isoformat(),
                                "check_out": check_out.isoformat(),
                                "created_at": check_in.isoformat(),
                            })

                            attendance_id += 1

                    current_day += timedelta(days=1)

    print("Attendance generation completed.")
    print(f"Total attendance records: {attendance_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_attendance()
