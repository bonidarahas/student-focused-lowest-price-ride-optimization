import re

from app.ai_gateway import AIGateway
from app.mcp_gateway import MCPGateway
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent


class PlannerAgent:
    def __init__(self):
        self.ai_gateway = AIGateway()
        self.mcp_gateway = MCPGateway()
        self.rag_agent = RAGAgent()
        self.sql_agent = SQLAgent()

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

        if any(keyword in message_lower for keyword in sql_keywords):
            return "sql"

        if any(keyword in message_lower for keyword in rag_keywords):
            return "rag"

        return "general_answer"

    def _extract_math_expression(self, message: str) -> str:
        allowed_chars = re.findall(r"[0-9\.\+\-\*\/\%\(\)\s]+", message)
        expression = "".join(allowed_chars).strip()

        return expression