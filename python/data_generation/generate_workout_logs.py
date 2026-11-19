
import csv
import random

import pandas as pd

from python.data_generation.config import RANDOM_SEED, RAW_DATA_DIR

random.seed(RANDOM_SEED)

EXERCISE_PROFILES = {
    1: (3, 5, 12, 60, 100),    # Bench Press
    2: (3, 5, 10, 60, 140),   # Squat
    3: (3, 3, 8, 80, 180),    # Deadlift
    4: (3, 5, 12, 0, 0),      # Pull Up
    5: (3, 8, 12, 15, 50),    # Shoulder Press
    6: (3, 8, 15, 5, 25),     # Bicep Curl
    7: (3, 8, 15, 5, 40),     # Tricep Pushdown
    8: (3, 8, 15, 40, 180),   # Leg Press
    9: (3, 20, 60, 0, 0),     # Plank
    10: (1, 1, 1, 0, 0),      # Running
}


def generate_workout_logs():
    sessions = pd.read_csv(RAW_DATA_DIR / "workout_sessions.csv")

    output_file = RAW_DATA_DIR / "workout_logs.csv"

    workout_id = 1

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "workout_id",
                "session_id",
                "exercise_id",
                "sets",
                "reps",
                "weight_kg",
                "created_at",
            ],
        )

        writer.writeheader()

        for session in sessions.itertuples(index=False):
            exercise_count = random.randint(3, 6)

            selected_exercises = random.sample(
                list(EXERCISE_PROFILES.keys()),
                exercise_count,
            )

            for exercise_id in selected_exercises:
                sets, min_reps, max_reps, min_weight, max_weight = (
                    EXERCISE_PROFILES[exercise_id]
                )

                if exercise_id == 10:
                    actual_sets = 1
                    reps = random.randint(10, 45)
                    weight = 0
                else:
                    actual_sets = sets
                    reps = random.randint(min_reps, max_reps)
                    weight = round(
                        random.uniform(min_weight, max_weight),
                        2,
                    ) if max_weight > 0 else 0

                writer.writerow({
                    "workout_id": workout_id,
                    "session_id": int(session.session_id),
                    "exercise_id": exercise_id,
                    "sets": actual_sets,
                    "reps": reps,
                    "weight_kg": weight,
                    "created_at": session.session_date,
                })

                workout_id += 1

    print("Workout logs generation completed.")
    print(f"Total workout logs: {workout_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_workout_logs()
