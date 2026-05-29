from tools.calculator import CalculatorTool


class MCPGateway:
    def __init__(self):
        self.tools = {
            "calculator": CalculatorTool()
        }

        self.agent_permissions = {
            "planner_agent": ["calculator"],
            "rag_agent": [],
            "sql_agent": []
        }

    def invoke_tool(self, agent_id: str, tool_name: str, tool_input: dict) -> dict:
        if tool_name not in self.tools:
            return {
                "status": "error",
                "error": f"Tool '{tool_name}' does not exist.",
                "result": None
            }

        allowed_tools = self.agent_permissions.get(agent_id, [])

        if tool_name not in allowed_tools:
            return {
                "status": "blocked",
                "error": f"Agent '{agent_id}' does not have permission to call tool '{tool_name}'.",
                "result": None
            }

        if tool_name == "calculator":
            expression = tool_input.get("expression", "")
            result = self.tools["calculator"].run(expression)

            return {
                "status": "success",
                "error": None,
                "result": result
            }

        return {
            "status": "error",
            "error": "Unknown tool execution path.",
            "result": None
        }