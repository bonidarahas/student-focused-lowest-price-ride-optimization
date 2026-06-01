import sqlite3
from pathlib import Path


DB_PATH = Path("database/uber_replica.db")


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS payments")
    cursor.execute("DROP TABLE IF EXISTS rides")
    cursor.execute("DROP TABLE IF EXISTS drivers")

    cursor.execute("""
        CREATE TABLE drivers (
            driver_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rating REAL NOT NULL,
            city TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE rides (
            ride_id INTEGER PRIMARY KEY,
            rider_name TEXT NOT NULL,
            driver_id INTEGER NOT NULL,
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            fare REAL NOT NULL,
            ride_date TEXT NOT NULL,
            is_student INTEGER NOT NULL,
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE payments (
            payment_id INTEGER PRIMARY KEY,
            ride_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
        )
    """)

    drivers = [
        (1, "Alex Johnson", 4.9, "Bridgeport"),
        (2, "Maria Lopez", 4.7, "Newark"),
        (3, "David Kim", 4.8, "Jersey City"),
        (4, "Sarah Patel", 4.6, "New York")
    ]

    rides = [
        (1, "Boni", 1, "University of Bridgeport", "Bridgeport Station", 12.50, "2026-05-01", 1),
        (2, "John", 2, "Newark Penn Station", "NJIT", 18.00, "2026-05-02", 1),
        (3, "Aisha", 3, "Jersey City", "Hoboken", 22.75, "2026-05-03", 0),
        (4, "Mark", 1, "Bridgeport Mall", "University of Bridgeport", 15.20, "2026-05-04", 1),
        (5, "Sophia", 4, "Times Square", "Brooklyn", 35.00, "2026-05-05", 0),
        (6, "Daniel", 2, "NJIT", "Newark Airport", 28.40, "2026-05-06", 1),
        (7, "Priya", 3, "Hoboken", "Jersey City", 16.90, "2026-05-07", 0),
        (8, "Emma", 1, "Bridgeport Station", "Seaside Park", 24.30, "2026-05-08", 1)
    ]

    payments = [
        (1, 1, 12.50, "card", "completed"),
        (2, 2, 18.00, "card", "completed"),
        (3, 3, 22.75, "paypal", "completed"),
        (4, 4, 15.20, "card", "completed"),
        (5, 5, 35.00, "apple_pay", "completed"),
        (6, 6, 28.40, "card", "completed"),
        (7, 7, 16.90, "cash", "pending"),
        (8, 8, 24.30, "card", "completed")
    ]

    cursor.executemany(
        "INSERT INTO drivers VALUES (?, ?, ?, ?)",
        drivers
    )

    cursor.executemany(
        "INSERT INTO rides VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rides
    )

    cursor.executemany(
        "INSERT INTO payments VALUES (?, ?, ?, ?, ?)",
        payments
    )

    connection.commit()
    connection.close()

    print("Database created successfully.")
    print(f"Database path: {DB_PATH}")


if __name__ == "__main__":
    create_database()