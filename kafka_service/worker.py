import json
import sqlite3
from datetime import datetime
from pathlib import Path

from confluent_kafka import Consumer, KafkaException


class KafkaBackgroundWorker:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        db_path: str = "database/uber_replica.db"
    ):
        self.db_path = Path(db_path)

        self.consumer = Consumer({
            "bootstrap.servers": bootstrap_servers,
            "group.id": "uber-background-worker",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False
        })

        self.topics = [
            "agent.requests",
            "agent.responses",
            "audit.logs"
        ]

        self._create_processed_events_table()

    def _create_processed_events_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                processed_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                kafka_partition INTEGER,
                kafka_offset INTEGER,
                processed_at TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def _store_event(
        self,
        topic: str,
        event_type: str,
        payload: dict,
        partition: int,
        offset: int
    ):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO processed_events (
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
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()
        connection.close()

    def process_event(self, message):
        event = json.loads(message.value().decode("utf-8"))

        event_type = event.get("event_type", "unknown")
        payload = event.get("payload", {})

        print("\nProcessing Kafka event")
        print(f"Topic: {message.topic()}")
        print(f"Event type: {event_type}")
        print(f"Payload: {payload}")

        self._store_event(
            topic=message.topic(),
            event_type=event_type,
            payload=payload,
            partition=message.partition(),
            offset=message.offset()
        )

    def run(self):
        self.consumer.subscribe(self.topics)

        print(f"Worker listening to topics: {self.topics}")

        try:
            while True:
                message = self.consumer.poll(timeout=1.0)

                if message is None:
                    continue

                if message.error():
                    raise KafkaException(message.error())

                try:
                    self.process_event(message)

                    # Commit only after successful processing.
                    self.consumer.commit(
                        message=message,
                        asynchronous=False
                    )

                    print("Event processed and offset committed.")

                except Exception as error:
                    print(f"Event processing failed: {error}")

        except KeyboardInterrupt:
            print("Worker stopped.")

        finally:
            self.consumer.close()


if __name__ == "__main__":
    KafkaBackgroundWorker().run()