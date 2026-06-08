import sqlite3
import json
from pathlib import Path
from datetime import datetime


class EventBus:
    """
    Kafka-style event bus simulation.

    Instead of sending events to Kafka topics,
    we store events in SQLite.

    Later, we can replace this with real Kafka.
    """

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)
        self._create_events_table()

    def _create_events_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def publish(self, topic: str, event_type: str, payload: dict):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO events (
                topic,
                event_type,
                payload,
                timestamp
            )
            VALUES (?, ?, ?, ?)
        """, (
            topic,
            event_type,
            json.dumps(payload),
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()
        connection.close()

    def get_events(self, limit: int = 50) -> list[dict]:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                event_id,
                topic,
                event_type,
                payload,
                timestamp
            FROM events
            ORDER BY event_id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        connection.close()

        events = []

        for row in rows:
            events.append({
                "event_id": row[0],
                "topic": row[1],
                "event_type": row[2],
                "payload": json.loads(row[3]),
                "timestamp": row[4]
            })

        return events