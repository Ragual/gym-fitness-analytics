
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


PAYMENT_METHODS = ["UPI", "CARD", "CASH", "NET_BANKING"]
PAYMENT_METHOD_WEIGHTS = [0.55, 0.25, 0.12, 0.08]


def generate_payments():
    memberships = pd.read_csv(RAW_DATA_DIR / "memberships.csv")

    end_date = date.fromisoformat(DATA_END_DATE)
    output_file = RAW_DATA_DIR / "payments.csv"

    payment_id = 1

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "payment_id",
                "membership_id",
                "amount",
                "payment_date",
                "payment_method",
                "payment_status",
                "transaction_reference",
                "created_at",
            ],
        )
        writer.writeheader()

        for membership in memberships.itertuples(index=False):
            start = date.fromisoformat(membership.start_date)
            finish = min(
                date.fromisoformat(membership.end_date),
                end_date,
            )

            if finish < start:
                continue

            duration_days = (finish - start).days + 1
            months = max(1, (duration_days + 29) // 30)

            # Match the four reference membership plans.
            plan_prices = {
                1: 999.00,
                2: 2699.00,
                3: 4999.00,
                4: 8999.00,
            }

            amount = plan_prices[int(membership.plan_id)]

            for month in range(months):
                payment_day = start + timedelta(days=month * 30)

                if payment_day > finish:
                    break

                if random.random() < 0.90:
                    status = "SUCCESS"
                elif random.random() < 0.60:
                    status = "FAILED"
                else:
                    status = "PENDING"

                payment_datetime = datetime.combine(
                    payment_day,
                    time(
                        hour=random.randint(6, 20),
                        minute=random.randint(0, 59),
                    ),
                )

                method = random.choices(
                    PAYMENT_METHODS,
                    weights=PAYMENT_METHOD_WEIGHTS,
                    k=1,
                )[0]

                writer.writerow({
                    "payment_id": payment_id,
                    "membership_id": int(membership.membership_id),
                    "amount": amount,
                    "payment_date": payment_datetime.isoformat(),
                    "payment_method": method,
                    "payment_status": status,
                    "transaction_reference": f"GYM-TXN-{payment_id:08d}",
                    "created_at": payment_datetime.isoformat(),
                })

                payment_id += 1

    print("Payment generation completed.")
    print(f"Total payment records: {payment_id - 1}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    generate_payments()
