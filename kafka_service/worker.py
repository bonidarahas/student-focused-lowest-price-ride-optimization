import json
import sqlite3
from datetime import datetime
from pathlib import Path

from confluent_kafka import Consumer


class KafkaBackgroundWorker:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        db_path: str = "database/uber_replica.db",
    ):
        self.db_path = Path(db_path)

        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": "uber-background-worker",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })

        self.topics = [
            "agent.requests",
            "agent.responses",
            "audit.logs",
            "ride.bookings",
            "ride.status",
        ]

        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_tables(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    processed_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    kafka_partition INTEGER NOT NULL,
                    kafka_offset INTEGER NOT NULL,
                    processed_at TEXT NOT NULL,
                    UNIQUE(topic, kafka_partition, kafka_offset)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ride_notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    rider_name TEXT NOT NULL,
                    driver_name TEXT NOT NULL,
                    final_price REAL NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(booking_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ride_status_notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    rider_name TEXT NOT NULL,
                    driver_name TEXT NOT NULL,
                    previous_status TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(
                        booking_id,
                        previous_status,
                        new_status
                    )
                )
            """)

            connection.commit()

    def _event_already_processed(
        self,
        topic: str,
        partition: int,
        offset: int,
    ) -> bool:
        with self._connect() as connection:
            row = connection.execute("""
                SELECT processed_id
                FROM processed_events
                WHERE topic = ?
                  AND kafka_partition = ?
                  AND kafka_offset = ?
            """, (
                topic,
                partition,
                offset,
            )).fetchone()

        return row is not None

    def _store_processed_event(
        self,
        topic: str,
        event_type: str,
        payload: dict,
        partition: int,
        offset: int,
    ) -> None:
        with self._connect() as connection:
            connection.execute("""
                INSERT OR IGNORE INTO processed_events (
                    topic,
                    event_type,
                    payload,
                    kafka_partition,
                    kafka_offset,
                    processed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                topic,
                event_type,
                json.dumps(payload),
                partition,
                offset,
                datetime.now().isoformat(timespec="seconds"),
            ))

            connection.commit()

    def _process_ride_booking(self, payload: dict) -> None:
        booking_id = payload.get("booking_id")
        rider_name = payload.get("rider_name", "Unknown rider")
        driver_name = payload.get("driver_name", "Unknown driver")
        final_price = float(payload.get("final_price", 0.0))
        status = payload.get("status", "unknown")

        if booking_id is None:
            raise ValueError(
                "Ride booking event is missing booking_id."
            )

        message = (
            f"Ride confirmed for {rider_name}. "
            f"Driver: {driver_name}. "
            f"Final price: ${final_price:.2f}. "
            f"Status: {status}."
        )

        with self._connect() as connection:
            connection.execute("""
                INSERT OR IGNORE INTO ride_notifications (
                    booking_id,
                    rider_name,
                    driver_name,
                    final_price,
                    status,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                rider_name,
                driver_name,
                final_price,
                status,
                message,
                datetime.now().isoformat(timespec="seconds"),
            ))

            connection.commit()

        print(f"Ride notification created: {message}")

    def _process_ride_status(self, payload: dict) -> None:
        required_fields = [
            "booking_id",
            "rider_name",
            "driver_name",
            "previous_status",
            "new_status",
            "message",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in payload
        ]

        if missing_fields:
            raise ValueError(
                "Ride status event is missing fields: "
                + ", ".join(missing_fields)
            )

        with self._connect() as connection:
            connection.execute("""
                INSERT OR IGNORE INTO ride_status_notifications (
                    booking_id,
                    rider_name,
                    driver_name,
                    previous_status,
                    new_status,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                payload["booking_id"],
                payload["rider_name"],
                payload["driver_name"],
                payload["previous_status"],
                payload["new_status"],
                payload["message"],
                datetime.now().isoformat(timespec="seconds"),
            ))

            connection.commit()

        print(
            "Ride status notification created: "
            f"{payload['message']}"
        )

    def process_event(self, message) -> None:
        topic = message.topic()
        partition = message.partition()
        offset = message.offset()

        if self._event_already_processed(
            topic=topic,
            partition=partition,
            offset=offset,
        ):
            print(
                "Skipping duplicate event: "
                f"{topic}[{partition}] offset {offset}"
            )
            return

        event = json.loads(
            message.value().decode("utf-8")
        )

        event_type = event.get("event_type", "unknown")
        payload = event.get("payload", {})

        print("\nProcessing Kafka event")
        print(f"Topic: {topic}")
        print(f"Partition: {partition}")
        print(f"Offset: {offset}")
        print(f"Event type: {event_type}")
        print(f"Payload: {payload}")

        if topic == "ride.bookings":
            self._process_ride_booking(payload)

        elif topic == "ride.status":
            self._process_ride_status(payload)

        self._store_processed_event(
            topic=topic,
            event_type=event_type,
            payload=payload,
            partition=partition,
            offset=offset,
        )

    def run(self) -> None:
        self.consumer.subscribe(self.topics)

        print("Kafka background worker started.")
        print(f"Listening to topics: {self.topics}")

        try:
            while True:
                message = self.consumer.poll(timeout=1.0)

                if message is None:
                    continue

                if message.error():
                    print(
                        f"Kafka consumer warning: "
                        f"{message.error()}"
                    )
                    continue

                try:
                    self.process_event(message)

                    self.consumer.commit(
                        message=message,
                        asynchronous=False,
                    )

                    print(
                        "Event processed and offset committed."
                    )

                except json.JSONDecodeError as error:
                    print(
                        f"Invalid JSON event: {error}"
                    )

                except Exception as error:
                    print(
                        f"Event processing failed: {error}"
                    )

        except KeyboardInterrupt:
            print("\nKafka worker stopped by user.")

        finally:
            self.consumer.close()
            print("Kafka consumer closed.")


if __name__ == "__main__":
    KafkaBackgroundWorker().run()