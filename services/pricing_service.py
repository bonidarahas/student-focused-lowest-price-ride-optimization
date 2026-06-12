import hashlib
import sqlite3
from pathlib import Path


class PricingService:
    """
    Student-focused ride price optimization.

    This version uses deterministic pricing:
    the same pickup/dropoff/driver combination always returns the same estimate.

    This is better for:
    - testing
    - evaluation
    - demos
    - predictable behavior
    """

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)
        self.student_discount_rate = 0.15

    def estimate_prices(
        self,
        pickup_location: str,
        dropoff_location: str,
        is_student: bool
    ) -> dict:
        drivers = self._get_available_drivers()

        if not drivers:
            return {
                "selected_option": None,
                "all_options": [],
                "reason": "No drivers available."
            }

        options = []

        for driver in drivers:
            driver_id = driver["driver_id"]
            driver_name = driver["name"]
            rating = driver["rating"]

            estimated_pickup_minutes = self._deterministic_pickup_time(
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                driver_id=driver_id
            )

            base_price = self._estimate_base_price(
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                rating=rating,
                estimated_pickup_minutes=estimated_pickup_minutes,
                driver_id=driver_id
            )

            discount_amount = 0.0

            if is_student:
                discount_amount = round(base_price * self.student_discount_rate, 2)

            final_price = round(base_price - discount_amount, 2)

            options.append({
                "driver_id": driver_id,
                "driver_name": driver_name,
                "rating": rating,
                "estimated_pickup_minutes": estimated_pickup_minutes,
                "base_price": base_price,
                "discount_amount": discount_amount,
                "final_price": final_price
            })

        selected_option = min(
            options,
            key=lambda option: (
                option["final_price"],
                option["estimated_pickup_minutes"],
                -option["rating"]
            )
        )

        if is_student:
            reason = "Lowest final price selected after applying verified student discount."
        else:
            reason = "Lowest available price selected."

        return {
            "selected_option": selected_option,
            "all_options": options,
            "reason": reason
        }

    def _get_available_drivers(self) -> list[dict]:
        if not self.db_path.exists():
            return []

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT driver_id, name, rating, city
            FROM drivers
            ORDER BY driver_id ASC
        """)

        rows = cursor.fetchall()
        connection.close()

        drivers = []

        for row in rows:
            drivers.append({
                "driver_id": row[0],
                "name": row[1],
                "rating": row[2],
                "city": row[3]
            })

        return drivers

    def _stable_number(self, text: str, min_value: int, max_value: int) -> int:
        """
        Converts text into a stable number in a range.

        Example:
        Same text always gives same number.
        """
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        number = int(digest[:8], 16)

        return min_value + (number % (max_value - min_value + 1))

    def _deterministic_pickup_time(
        self,
        pickup_location: str,
        dropoff_location: str,
        driver_id: int
    ) -> int:
        seed_text = f"{pickup_location}|{dropoff_location}|{driver_id}|pickup_time"
        return self._stable_number(seed_text, 3, 12)

    def _estimate_base_price(
        self,
        pickup_location: str,
        dropoff_location: str,
        rating: float,
        estimated_pickup_minutes: int,
        driver_id: int
    ) -> float:
        seed_text = f"{pickup_location}|{dropoff_location}|{driver_id}|price"
        simulated_distance_miles = self._stable_number(seed_text, 2, 14)

        base_fare = 6.50
        per_mile_rate = 1.65
        distance_cost = simulated_distance_miles * per_mile_rate

        rating_premium = max(0, rating - 4.5) * 1.75

        pickup_discount = 0.0
        if estimated_pickup_minutes > 8:
            pickup_discount = 0.75

        price = base_fare + distance_cost + rating_premium - pickup_discount

        return round(price, 2)