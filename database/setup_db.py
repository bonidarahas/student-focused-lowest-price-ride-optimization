import sqlite3

from services.pricing_service import PricingService


def create_test_drivers(database_path) -> None:
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


def create_pricing_service(tmp_path) -> PricingService:
    database_path = tmp_path / "test_uber.db"

    create_test_drivers(database_path)

    return PricingService(
        db_path=str(database_path)
    )


def test_student_discount_is_applied(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    selected_option = result["selected_option"]

    assert selected_option is not None
    assert selected_option["discount_amount"] > 0
    assert selected_option["final_price"] < selected_option["base_price"]


def test_non_student_has_no_discount(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=False,
    )

    selected_option = result["selected_option"]

    assert selected_option is not None
    assert selected_option["discount_amount"] == 0
    assert selected_option["final_price"] == selected_option["base_price"]


def test_same_route_returns_same_prices(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    first_result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    second_result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    assert first_result["all_options"] == second_result["all_options"]
    assert first_result["selected_option"] == second_result["selected_option"]


def test_lowest_price_is_selected(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="Bridgeport",
        dropoff_location="New Haven",
        is_student=True,
    )

    all_options = result["all_options"]
    selected_option = result["selected_option"]

    assert all_options
    assert selected_option is not None

    lowest_price = min(
        option["final_price"]
        for option in all_options
    )

    assert selected_option["final_price"] == lowest_price


def test_price_options_have_required_fields(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="NJIT",
        dropoff_location="Newark Airport",
        is_student=True,
    )

    required_fields = {
        "driver_id",
        "driver_name",
        "rating",
        "estimated_pickup_minutes",
        "base_price",
        "discount_amount",
        "final_price",
    }

    assert result["all_options"]

    for option in result["all_options"]:
        assert required_fields.issubset(option.keys())


def test_student_price_is_not_negative(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="A",
        dropoff_location="B",
        is_student=True,
    )

    assert result["all_options"]

    for option in result["all_options"]:
        assert option["base_price"] >= 0
        assert option["discount_amount"] >= 0
        assert option["final_price"] >= 0


def test_student_reason_mentions_discount(tmp_path):
    pricing_service = create_pricing_service(tmp_path)

    result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    assert "student" in result["reason"].lower()
    assert "discount" in result["reason"].lower()


def test_no_drivers_returns_empty_result(tmp_path):
    database_path = tmp_path / "test_uber.db"

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE drivers (
                driver_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rating REAL NOT NULL,
                city TEXT NOT NULL
            )
        """)

        connection.commit()

    pricing_service = PricingService(
        db_path=str(database_path)
    )

    result = pricing_service.estimate_prices(
        pickup_location="Hamilton",
        dropoff_location="Hudson",
        is_student=True,
    )

    assert result["selected_option"] is None
    assert result["all_options"] == []
    assert result["reason"] == "No drivers available."