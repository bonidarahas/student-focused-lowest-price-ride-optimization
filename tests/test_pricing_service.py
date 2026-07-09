import sqlite3

from services.ride_booking_service import RideBookingService


def create_test_database(database_path) -> None:
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rating REAL NOT NULL,
                city TEXT NOT NULL
            )
        """)

        cursor.executemany("""
            INSERT INTO drivers (
                driver_id,
                name,
                rating,
                city
            )
            VALUES (?, ?, ?, ?)
        """, [
            (1, "Sarah Patel", 4.9, "Hamilton"),
            (2, "Alex Johnson", 4.8, "Hudson"),
            (3, "David Kim", 4.7, "Bridgeport"),
        ])

        connection.commit()


def create_booking_service(tmp_path) -> RideBookingService:
    database_path = tmp_path / "test_uber.db"

    create_test_database(database_path)

    return RideBookingService(
        db_path=str(database_path)
    )


def test_book_ride_creates_confirmed_booking(tmp_path):
    service = create_booking_service(tmp_path)

    result = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    assert result["booking_id"] > 0
    assert result["rider_name"] == "Boni"
    assert result["status"] == "confirmed"
    assert result["final_price"] > 0
    assert result["driver_name"]


def test_booking_is_saved_to_database(tmp_path):
    service = create_booking_service(tmp_path)

    result = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    stored_booking = service.get_booking(
        result["booking_id"]
    )

    assert stored_booking is not None
    assert stored_booking["booking_id"] == result["booking_id"]
    assert stored_booking["rider_name"] == "Boni"
    assert stored_booking["pickup_location"] == "Hamilton"
    assert stored_booking["dropoff_location"] == "Hudson"
    assert stored_booking["status"] == "confirmed"


def test_get_missing_booking_returns_none(tmp_path):
    service = create_booking_service(tmp_path)

    result = service.get_booking(9999)

    assert result is None


def test_list_bookings_returns_created_rides(tmp_path):
    service = create_booking_service(tmp_path)

    service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    service.book_ride(
        rider_name="Alex",
        pickup_location="Bridgeport",
        dropoff_location="New Haven",
        is_student=False,
    )

    bookings = service.list_bookings()

    assert len(bookings) == 2
    assert bookings[0]["rider_name"] == "Alex"
    assert bookings[1]["rider_name"] == "Boni"


def test_confirmed_ride_can_move_to_driver_arriving(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    result = service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="driver_arriving",
    )

    assert result["success"] is True
    assert result["previous_status"] == "confirmed"
    assert result["new_status"] == "driver_arriving"


def test_driver_arriving_can_move_to_in_progress(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="driver_arriving",
    )

    result = service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="in_progress",
    )

    assert result["success"] is True
    assert result["previous_status"] == "driver_arriving"
    assert result["new_status"] == "in_progress"


def test_in_progress_can_move_to_completed(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="driver_arriving",
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="in_progress",
    )

    result = service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="completed",
    )

    assert result["success"] is True
    assert result["new_status"] == "completed"

    stored_booking = service.get_booking(
        booking["booking_id"]
    )

    assert stored_booking["status"] == "completed"


def test_confirmed_ride_can_be_cancelled(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    result = service.cancel_booking(
        booking["booking_id"]
    )

    assert result["success"] is True
    assert result["new_status"] == "cancelled"


def test_completed_ride_cannot_be_cancelled(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="driver_arriving",
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="in_progress",
    )

    service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="completed",
    )

    result = service.cancel_booking(
        booking["booking_id"]
    )

    assert result["success"] is False
    assert "invalid status transition" in result["message"].lower()


def test_cancelled_ride_cannot_start(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    service.cancel_booking(
        booking["booking_id"]
    )

    result = service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="in_progress",
    )

    assert result["success"] is False
    assert "invalid status transition" in result["message"].lower()


def test_invalid_status_is_rejected(tmp_path):
    service = create_booking_service(tmp_path)

    booking = service.book_ride(
        rider_name="Boni",
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    result = service.update_booking_status(
        booking_id=booking["booking_id"],
        new_status="flying",
    )

    assert result["success"] is False
    assert "invalid ride status" in result["message"].lower()


def test_missing_booking_status_update_fails(tmp_path):
    service = create_booking_service(tmp_path)

    result = service.update_booking_status(
        booking_id=9999,
        new_status="cancelled",
    )

    assert result["success"] is False
    assert "not found" in result["message"].lower()