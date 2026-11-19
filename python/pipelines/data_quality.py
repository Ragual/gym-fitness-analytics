
from python.database import get_connection


CHECKS = {
    "Members without memberships": """
        SELECT COUNT(*)
        FROM members m
        LEFT JOIN memberships ms ON m.member_id = ms.member_id
        WHERE ms.membership_id IS NULL;
    """,
    "Memberships without members": """
        SELECT COUNT(*)
        FROM memberships ms
        LEFT JOIN members m ON ms.member_id = m.member_id
        WHERE m.member_id IS NULL;
    """,
    "Attendance without members": """
        SELECT COUNT(*)
        FROM attendance a
        LEFT JOIN members m ON a.member_id = m.member_id
        WHERE m.member_id IS NULL;
    """,
    "Payments without memberships": """
        SELECT COUNT(*)
        FROM payments p
        LEFT JOIN memberships ms ON p.membership_id = ms.membership_id
        WHERE ms.membership_id IS NULL;
    """,
    "Workout sessions without members": """
        SELECT COUNT(*)
        FROM workout_sessions ws
        LEFT JOIN members m ON ws.member_id = m.member_id
        WHERE m.member_id IS NULL;
    """,
    "Workout logs without sessions": """
        SELECT COUNT(*)
        FROM workout_logs wl
        LEFT JOIN workout_sessions ws ON wl.session_id = ws.session_id
        WHERE ws.session_id IS NULL;
    """,
    "Workout logs without exercises": """
        SELECT COUNT(*)
        FROM workout_logs wl
        LEFT JOIN exercises e ON wl.exercise_id = e.exercise_id
        WHERE e.exercise_id IS NULL;
    """,
    "Invalid attendance durations": """
        SELECT COUNT(*)
        FROM attendance
        WHERE check_out IS NOT NULL
          AND check_out <= check_in;
    """,
    "Invalid membership date ranges": """
        SELECT COUNT(*)
        FROM memberships
        WHERE end_date < start_date;
    """,
    "Invalid workout weights": """
        SELECT COUNT(*)
        FROM workout_logs
        WHERE weight_kg < 0;
    """,
}


def run_quality_checks():
    print("\n========== DATA QUALITY REPORT ==========\n")

    failed_checks = 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for check_name, query in CHECKS.items():
                cursor.execute(query)
                issue_count = cursor.fetchone()[0]

                status = "PASS" if issue_count == 0 else "CHECK"

                if issue_count > 0:
                    failed_checks += 1

                print(
                    f"{status}: {check_name} "
                    f"| Issues: {issue_count:,}"
                )

    print("\n========== SUMMARY ==========")
    print(f"Checks executed: {len(CHECKS)}")
    print(f"Checks requiring attention: {failed_checks}")


if __name__ == "__main__":
    run_quality_checks()
