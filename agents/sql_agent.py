import sqlite3
from pathlib import Path


class SQLAgent:
    """
    SQL Agent for querying the Uber Replica SQLite database.

    This version uses safe predefined query patterns.
    Later, we can upgrade it to generate SQL using an LLM,
    then validate the SQL before execution.
    """

    def __init__(self, db_path: str = "database/uber_replica.db"):
        self.db_path = Path(db_path)

    def answer_question(self, question: str) -> dict:
        question_lower = question.lower()

        if not self.db_path.exists():
            return {
                "answer": "Database not found. Run: python -m database.setup_db",
                "sql": None,
                "rows": []
            }

        if "driver" in question_lower and ("most" in question_lower or "highest" in question_lower or "earned" in question_lower):
            sql = """
                SELECT 
                    drivers.name,
                    SUM(rides.fare) AS total_earnings
                FROM rides
                JOIN drivers ON rides.driver_id = drivers.driver_id
                GROUP BY drivers.driver_id
                ORDER BY total_earnings DESC
                LIMIT 1
            """

            rows = self._run_select(sql)

            if rows:
                name = rows[0][0]
                earnings = rows[0][1]

                return {
                    "answer": f"The highest earning driver is {name} with total ride earnings of ${earnings:.2f}.",
                    "sql": sql.strip(),
                    "rows": rows
                }

        if "total" in question_lower and ("revenue" in question_lower or "earnings" in question_lower or "fare" in question_lower):
            sql = """
                SELECT SUM(fare) AS total_revenue
                FROM rides
            """

            rows = self._run_select(sql)

            if rows:
                total = rows[0][0]

                return {
                    "answer": f"Total ride revenue is ${total:.2f}.",
                    "sql": sql.strip(),
                    "rows": rows
                }

        if "student" in question_lower and ("ride" in question_lower or "rides" in question_lower or "count" in question_lower):
            sql = """
                SELECT COUNT(*) AS student_ride_count
                FROM rides
                WHERE is_student = 1
            """

            rows = self._run_select(sql)

            if rows:
                count = rows[0][0]

                return {
                    "answer": f"There are {count} student rides in the database.",
                    "sql": sql.strip(),
                    "rows": rows
                }

        if "average" in question_lower and ("fare" in question_lower or "ride" in question_lower):
            sql = """
                SELECT AVG(fare) AS average_fare
                FROM rides
            """

            rows = self._run_select(sql)

            if rows:
                average = rows[0][0]

                return {
                    "answer": f"The average ride fare is ${average:.2f}.",
                    "sql": sql.strip(),
                    "rows": rows
                }

        if "top drivers" in question_lower or "drivers by earnings" in question_lower:
            sql = """
                SELECT 
                    drivers.name,
                    SUM(rides.fare) AS total_earnings
                FROM rides
                JOIN drivers ON rides.driver_id = drivers.driver_id
                GROUP BY drivers.driver_id
                ORDER BY total_earnings DESC
            """

            rows = self._run_select(sql)

            if rows:
                formatted = [
                    f"{index + 1}. {row[0]} - ${row[1]:.2f}"
                    for index, row in enumerate(rows)
                ]

                return {
                    "answer": "Drivers by earnings:\n" + "\n".join(formatted),
                    "sql": sql.strip(),
                    "rows": rows
                }

        return {
            "answer": (
                "I can answer SQL questions like: "
                "'Which driver earned the most?', "
                "'What is total revenue?', "
                "'How many student rides?', "
                "'What is the average fare?', "
                "or 'Show top drivers by earnings.'"
            ),
            "sql": None,
            "rows": []
        }

    def _run_select(self, sql: str) -> list:
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(sql)
        rows = cursor.fetchall()

        connection.close()

        return rows