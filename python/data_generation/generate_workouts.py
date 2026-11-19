
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

TRAINER_IDS = [1, 2, 3, 4, 5]


def generate_workouts():
    attendance = pd.read_csv(RAW_DATA_DIR / "attendance.csv")

    end_date = date.fromisoformat(DATA_END_DATE)
    output_file = RAW_DATA_DIR / "workout_sessions.csv"

    session_id = 1

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "session_id",
                "member_id",
                "trainer_id",
                "session_date",
                "duration_minutes",
                "notes",
            ],
        )

        writer.writeheader()

        for record in attendance.itertuples(index=False):
            session_datetime = datetime.fromisoformat(record.check_in)

            # Most visits are self-guided; some have trainer supervision.
            trainer_id = (
                random.choice(TRAINER_IDS)
                if random.random() < 0.35
                else ""
            )

            duration = random.randint(30, 120)

            notes = random.choice([
                "Strength training",
                "Cardio session",
                "Full body workout",
                "Upper body workout",
                "Lower body workout",
                "Functional training",
                "Personal training session",
                "General fitness",
            ])

            writer.writerow({
                "session_id": session_id,
                "member_id": int(record.member_id),
                "trainer_id": trainer_id,
                "session_date": session_datetime.isoformat(),
                "duration_minutes": duration,
                "notes": notes,
            })

            session_id += 1

    print("Workout session generation completed.")
    print(f"Total workout sessions: {session_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_workouts()
