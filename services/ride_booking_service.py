import sqlite3
from datetime import datetime
from pathlib import Path

from services.pricing_service import PricingService


class RideBookingService:
    """
    Handles ride estimation, booking creation, booking retrieval,
    listing bookings, and ride status updates.
    """

    ALLOWED_STATUSES = {
        "confirmed",
        "driver_arriving",
        "in_progress",
        "completed",
        "cancelled",
    }

    VALID_STATUS_TRANSITIONS = {
        "confirmed": {"driver_arriving", "cancelled"},
        "driver_arriving": {"in_progress", "cancelled"},
        "in_progress": {"completed"},
        "completed": set(),
        "cancelled": set(),
    }

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)
        self.pricing_service = PricingService(db_path=db_path)
        self._create_bookings_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_bookings_table(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute("""
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

    def estimate_ride(
        self,
        rider_name: str,
        pickup_location: str,
        dropoff_location: str,
        is_student: bool,
    ) -> dict:
        """
        Calculates all driver price options and selects the cheapest option.

        rider_name is accepted so the method matches the booking API,
        although pricing currently does not depend on the rider's name.
        """
        del rider_name

        return self.pricing_service.estimate_prices(
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            is_student=is_student,
        )

    def book_ride(
        self,
        rider_name: str,
        pickup_location: str,
        dropoff_location: str,
        is_student: bool,
    ) -> dict:
        pricing_result = self.estimate_ride(
            rider_name=rider_name,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            is_student=is_student,
        )

        selected_option = pricing_result.get("selected_option")

        if selected_option is None:
            return {
                "booking_id": -1,
                "rider_name": rider_name,
                "driver_id": -1,
                "driver_name": "N/A",
                "pickup_location": pickup_location,
                "dropoff_location": dropoff_location,
                "is_student": is_student,
                "base_price": 0.0,
                "discount_amount": 0.0,
                "final_price": 0.0,
                "status": "failed",
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "reason": pricing_result.get(
                    "reason",
                    "No suitable ride option was available.",
                ),
            }

        created_at = datetime.now().isoformat(timespec="seconds")

        with self._connect() as connection:
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
                created_at,
            ))

            booking_id = cursor.lastrowid
            connection.commit()

        return {
            "booking_id": booking_id,
            "rider_name": rider_name,
            "driver_id": selected_option["driver_id"],
            "driver_name": selected_option["driver_name"],
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "is_student": is_student,
            "base_price": selected_option["base_price"],
            "discount_amount": selected_option["discount_amount"],
            "final_price": selected_option["final_price"],
            "status": "confirmed",
            "created_at": created_at,
            "reason": pricing_result["reason"],
        }

    def get_booking(self, booking_id: int) -> dict | None:
        if not self.db_path.exists():
            return None

        with self._connect() as connection:
            row = connection.execute("""
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
                WHERE booking_id = ?
            """, (booking_id,)).fetchone()

        if row is None:
            return None

        return self._row_to_booking(row)

    def list_bookings(self, limit: int = 50) -> list[dict]:
        if not self.db_path.exists():
            return []

        safe_limit = max(1, min(limit, 500))

        with self._connect() as connection:
            rows = connection.execute("""
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
            """, (safe_limit,)).fetchall()

        return [self._row_to_booking(row) for row in rows]

    def update_booking_status(
        self,
        booking_id: int,
        new_status: str,
    ) -> dict:
        normalized_status = new_status.strip().lower()

        if normalized_status not in self.ALLOWED_STATUSES:
            return {
                "success": False,
                "message": (
                    f"Invalid ride status '{new_status}'. "
                    f"Allowed statuses: {sorted(self.ALLOWED_STATUSES)}"
                ),
            }

        booking = self.get_booking(booking_id)

        if booking is None:
            return {
                "success": False,
                "message": f"Booking {booking_id} was not found.",
            }

        previous_status = booking["status"]

        if normalized_status == previous_status:
            return {
                "success": False,
                "message": (
                    f"Ride {booking_id} is already in status "
                    f"'{previous_status}'."
                ),
            }

        allowed_next_statuses = self.VALID_STATUS_TRANSITIONS.get(
            previous_status,
            set(),
        )

        if normalized_status not in allowed_next_statuses:
            return {
                "success": False,
                "message": (
                    f"Invalid status transition from '{previous_status}' "
                    f"to '{normalized_status}'. Allowed next statuses: "
                    f"{sorted(allowed_next_statuses)}"
                ),
            }

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE ride_bookings
                SET status = ?
                WHERE booking_id = ?
            """, (
                normalized_status,
                booking_id,
            ))

            connection.commit()

        return {
            "success": True,
            "booking_id": booking_id,
            "rider_name": booking["rider_name"],
            "driver_name": booking["driver_name"],
            "previous_status": previous_status,
            "new_status": normalized_status,
            "message": (
                f"Ride {booking_id} status changed from "
                f"'{previous_status}' to '{normalized_status}'."
            ),
        }

    def cancel_booking(self, booking_id: int) -> dict:
        """
        Convenience method for cancelling a ride.
        """
        return self.update_booking_status(
            booking_id=booking_id,
            new_status="cancelled",
        )

    @staticmethod
    def _row_to_booking(row: sqlite3.Row) -> dict:
        return {
            "booking_id": row["booking_id"],
            "rider_name": row["rider_name"],
            "driver_id": row["driver_id"],
            "driver_name": row["driver_name"],
            "pickup_location": row["pickup_location"],
            "dropoff_location": row["dropoff_location"],
            "is_student": bool(row["is_student"]),
            "base_price": row["base_price"],
            "discount_amount": row["discount_amount"],
            "final_price": row["final_price"],
            "status": row["status"],
            "created_at": row["created_at"],
        }