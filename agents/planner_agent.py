import re

from app.ai_gateway import AIGateway
from app.mcp_gateway import MCPGateway

from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent

from services.ride_booking_service import RideBookingService


class PlannerAgent:
    def __init__(self):
        self.ai_gateway = AIGateway()
        self.mcp_gateway = MCPGateway()
        self.rag_agent = RAGAgent()
        self.sql_agent = SQLAgent()
        self.ride_booking_service = RideBookingService()

    def handle_message(self, message: str) -> dict:
        steps = []

        steps.append({
            "agent": "planner_agent",
            "action": "received_message",
            "details": "Planner received the user message."
        })

        route = self._choose_route(message)

        steps.append({
            "agent": "planner_agent",
            "action": "selected_route",
            "details": route
        })

        if route == "calculator":
            expression = self._extract_math_expression(message)

            steps.append({
                "agent": "planner_agent",
                "action": "extracted_expression",
                "details": expression
            })

            tool_result = self.mcp_gateway.invoke_tool(
                agent_id="planner_agent",
                tool_name="calculator",
                tool_input={"expression": expression}
            )

            steps.append({
                "agent": "mcp_gateway",
                "action": "tool_invoked",
                "details": f"calculator status: {tool_result['status']}"
            })

            if tool_result["status"] == "success":
                return {
                    "answer": f"The answer is {tool_result['result']}.",
                    "route": route,
                    "steps": steps
                }

            return {
                "answer": f"Tool error: {tool_result['error']}",
                "route": route,
                "steps": steps
            }

        if route == "rag":
            rag_result = self.rag_agent.answer_question(message)

            steps.append({
                "agent": "rag_agent",
                "action": "searched_documents",
                "details": f"sources: {rag_result['sources']}"
            })

            return {
                "answer": rag_result["answer"],
                "route": route,
                "steps": steps
            }

        if route == "sql":
            sql_result = self.sql_agent.answer_question(message)

            steps.append({
                "agent": "sql_agent",
                "action": "executed_sql_query",
                "details": sql_result["sql"] if sql_result["sql"] else "No SQL query executed."
            })

            return {
                "answer": sql_result["answer"],
                "route": route,
                "steps": steps
            }

        if route == "ride_booking":
            ride_details = self._extract_ride_details(message)

            steps.append({
                "agent": "planner_agent",
                "action": "extracted_ride_details",
                "details": (
                    f"pickup: {ride_details['pickup_location']}, "
                    f"dropoff: {ride_details['dropoff_location']}, "
                    f"is_student: {ride_details['is_student']}"
                )
            })

            booking_result = self.ride_booking_service.book_ride(
                rider_name=ride_details["rider_name"],
                pickup_location=ride_details["pickup_location"],
                dropoff_location=ride_details["dropoff_location"],
                is_student=ride_details["is_student"]
            )

            steps.append({
                "agent": "ride_booking_service",
                "action": "created_ride_booking",
                "details": (
                    f"booking_id: {booking_result['booking_id']}, "
                    f"status: {booking_result['status']}"
                )
            })

            return {
                "answer": (
                    f"Ride booked successfully. "
                    f"Driver: {booking_result['driver_name']}. "
                    f"Final price: ${booking_result['final_price']}. "
                    f"Status: {booking_result['status']}. "
                    f"Reason: {booking_result['reason']}"
                ),
                "route": route,
                "steps": steps
            }

        answer = self.ai_gateway.generate_response(message)

        steps.append({
            "agent": "ai_gateway",
            "action": "generated_response",
            "details": "AI Gateway generated a response."
        })

        return {
            "answer": answer,
            "route": route,
            "steps": steps
        }

    def _choose_route(self, message: str) -> str:
        message_lower = message.lower()

        calculator_keywords = [
            "calculate",
            "solve",
            "+",
            "-",
            "*",
            "/",
            "%"
        ]

        ride_booking_keywords = [
            "book ride",
            "book me",
            "ride from",
            "student ride",
            "pickup",
            "dropoff",
            "need a ride",
            "get me a ride",
            "schedule a ride"
        ]

        sql_keywords = [
            "revenue",
            "earnings",
            "earned",
            "driver earned",
            "top drivers",
            "average fare",
            "student rides",
            "how many student",
            "count student",
            "total fare",
            "rides database",
            "how many rides",
            "which driver",
            "highest earning",
            "most money",
            "total rides",
            "payment",
            "payments",
            "fare",
            "database"
        ]

        rag_keywords = [
            "student discount policy",
            "discount policy",
            "policy",
            "cancel",
            "cancellation",
            "driver match",
            "driver matched",
            "matched",
            "matching policy",
            "lowest price",
            "premium ride",
            "premium rides",
            "qualify",
            "student discount"
        ]

        has_number = any(char.isdigit() for char in message)

        if has_number and any(keyword in message_lower for keyword in calculator_keywords):
            return "calculator"

        if "ride" in message_lower and any(keyword in message_lower for keyword in ride_booking_keywords):
            return "ride_booking"

        if any(keyword in message_lower for keyword in sql_keywords):
            return "sql"

        if any(keyword in message_lower for keyword in rag_keywords):
            return "rag"

        return "general_answer"

    def _extract_math_expression(self, message: str) -> str:
        allowed_chars = re.findall(r"[0-9\.\+\-\*\/\%\(\)\s]+", message)
        expression = "".join(allowed_chars).strip()

        return expression

    def _extract_ride_details(self, message: str) -> dict:
        """
        Parses simple natural-language ride requests.

        Supported examples:
        - "Book me a student ride from Hamilton to Hudson"
        - "Book ride from Newark Penn Station to NJIT"
        - "I need a ride from Bridgeport Station to University of Bridgeport"
        """

        message_lower = message.lower()

        is_student = any(
            keyword in message_lower
            for keyword in ["student", "college", "university"]
        )

        rider_name = "Boni"

        pickup_location = "Unknown Pickup"
        dropoff_location = "Unknown Dropoff"

        if " from " in message_lower and " to " in message_lower:
            try:
                after_from_original = message.split(" from ", 1)[1]
                pickup_original, dropoff_original = after_from_original.split(" to ", 1)

                pickup_location = pickup_original.strip(" .,!?:;")
                dropoff_location = dropoff_original.strip(" .,!?:;")
            except Exception:
                pickup_location = "Unknown Pickup"
                dropoff_location = "Unknown Dropoff"

        return {
            "rider_name": rider_name,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "is_student": is_student
        }