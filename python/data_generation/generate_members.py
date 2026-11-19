
import csv
import random
from datetime import date, datetime, timedelta

from faker import Faker

from python.data_generation.config import (
    DATA_END_DATE,
    DATA_START_DATE,
    NUM_MEMBERS,
    RANDOM_SEED,
    RAW_DATA_DIR,
)


fake = Faker()
fake.seed_instance(RANDOM_SEED)
random.seed(RANDOM_SEED)


def generate_members():
    start_date = date.fromisoformat(DATA_START_DATE)
    end_date = date.fromisoformat(DATA_END_DATE)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = RAW_DATA_DIR / "members.csv"

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "member_id",
                "full_name",
                "email",
                "date_of_birth",
                "gender",
                "join_date",
                "created_at",
            ],
        )

        writer.writeheader()

        for member_id in range(1, NUM_MEMBERS + 1):
            join_offset = random.randint(
                0,
                (end_date - start_date).days,
            )

            join_date = start_date + timedelta(
                days=join_offset
            )

            birth_date = fake.date_of_birth(
                minimum_age=18,
                maximum_age=65,
            )

            writer.writerow({
                "member_id": member_id,
                "full_name": fake.name(),
                "email": f"member{member_id}@gymexample.com",
                "date_of_birth": birth_date.isoformat(),
                "gender": random.choice([
                    "Male",
                    "Female",
                ]),
                "join_date": join_date.isoformat(),
                "created_at": datetime.combine(
                    join_date,
                    datetime.min.time(),
                ).isoformat(sep=" "),
            })

    print("Member generation completed.")
    print(f"Total members: {NUM_MEMBERS}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_members()
