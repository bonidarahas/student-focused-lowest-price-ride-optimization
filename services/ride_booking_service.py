import sqlite3
from pathlib import Path
from datetime import datetime

from services.pricing_service import PricingService


class RideBookingService:
    """
    Simulates creating a ride booking using the best optimized price.
    """

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)
        self.pricing_service = PricingService(db_path=db_path)
        self._create_bookings_table()

    def _create_bookings_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ride_bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rider_name TEXT NOT NULL,
                driver_id INTEGER NOT NULL,
                driver_name TEXT NOT NULL,
                pickup_location TEXT NOT NULL,
                dropoff_location TEXT NOT NULL,
                is_student INTEGER NOT NULL,
                base_price REAL NOT NULL,
                discount_amount REAL NOT NULL,
                final_price REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def estimate_ride(
        self,
        rider_name: str,
        pickup_location: str,
        dropoff_location: str,
        is_student: bool
    ) -> dict:
        pricing_result = self.pricing_service.estimate_prices(
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            is_student=is_student
        )

        return pricing_result

    def book_ride(
        self,
        rider_name: str,
        pickup_location: str,
        dropoff_location: str,
        is_student: bool
    ) -> dict:
        pricing_result = self.estimate_ride(
            rider_name=rider_name,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            is_student=is_student
        )

        selected_option = pricing_result["selected_option"]

        if selected_option is None:
            return {
                "booking_id": -1,
                "rider_name": rider_name,
                "driver_id": -1,
                "driver_name": "N/A",
                "pickup_location": pickup_location,
                "dropoff_location": dropoff_location,
                "final_price": 0.0,
                "status": "failed",
                "reason": pricing_result["reason"]
            }

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ride_bookings (
                rider_name,
                driver_id,
                driver_name,
                pickup_location,
                dropoff_location,
                is_student,
                base_price,
                discount_amount,
                final_price,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rider_name,
            selected_option["driver_id"],
            selected_option["driver_name"],
            pickup_location,
            dropoff_location,
            1 if is_student else 0,
            selected_option["base_price"],
            selected_option["discount_amount"],
            selected_option["final_price"],
            "confirmed",
            datetime.now().isoformat(timespec="seconds")
        ))

        booking_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return {
            "booking_id": booking_id,
            "rider_name": rider_name,
            "driver_id": selected_option["driver_id"],
            "driver_name": selected_option["driver_name"],
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "final_price": selected_option["final_price"],
            "status": "confirmed",
            "reason": pricing_result["reason"]
        }

    def list_bookings(self, limit: int = 50) -> list[dict]:
        if not self.db_path.exists():
            return []

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                booking_id,
                rider_name,
                driver_id,
                driver_name,
                pickup_location,
                dropoff_location,
                is_student,
                base_price,
                discount_amount,
                final_price,
                status,
                created_at
            FROM ride_bookings
            ORDER BY booking_id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        connection.close()

        bookings = []

        for row in rows:
            bookings.append({
                "booking_id": row[0],
                "rider_name": row[1],
                "driver_id": row[2],
                "driver_name": row[3],
                "pickup_location": row[4],
                "dropoff_location": row[5],
                "is_student": bool(row[6]),
                "base_price": row[7],
                "discount_amount": row[8],
                "final_price": row[9],
                "status": row[10],
                "created_at": row[11]
            })

        return bookings