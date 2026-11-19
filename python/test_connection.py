from python.database import get_connection

try:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            print("Database connection successful!")
            print(cursor.fetchone())
except Exception as error:
    print("Database connection failed:")
    print(error)