import sqlite3
from pathlib import Path
from datetime import datetime


LOG_DB_PATH = Path("database/uber_replica.db")


class AgentLogger:
    """
    Stores agent actions in the SQLite database.
    """

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)
        self._create_logs_table()

    def _create_logs_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                route TEXT NOT NULL,
                agent TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def log_steps(self, user_id: str, route: str, steps: list):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        for step in steps:
            cursor.execute("""
                INSERT INTO agent_logs (
                    user_id,
                    route,
                    agent,
                    action,
                    details,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                route,
                step.get("agent", ""),
                step.get("action", ""),
                step.get("details", ""),
                datetime.now().isoformat(timespec="seconds")
            ))

        connection.commit()
        connection.close()

    def get_logs(self, limit: int = 50) -> list[dict]:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT 
                log_id,
                user_id,
                route,
                agent,
                action,
                details,
                timestamp
            FROM agent_logs
            ORDER BY log_id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        connection.close()

        logs = []

        for row in rows:
            logs.append({
                "log_id": row[0],
                "user_id": row[1],
                "route": row[2],
                "agent": row[3],
                "action": row[4],
                "details": row[5],
                "timestamp": row[6]
            })

        return logs