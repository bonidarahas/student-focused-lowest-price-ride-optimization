from fastapi import FastAPI
from app.schemas import (ChatRequest, ChatResponse,ToolInvokeRequest , ToolInvokeResponse)
from agents.planner_agent import PlannerAgent
from app.mcp_gateway import MCPGateway


app = FastAPI(
    title="AgentMesh Lite",
    description="Mini Uber-style AI Agent Platform",
    version="0.2.0"
)

planner_agent = PlannerAgent()
mcp_gateway = MCPGateway()



@app.get("/")
def home():
    return {
        "message": "AgentMesh Lite is running.",
        "docs": "Go to /docs to test the API.",
        "VERSION": "0.2.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = planner_agent.handle_message(request.message)

    return ChatResponse(
        user_id=request.user_id,
        answer=result["answer"],
        route=result["route"],
        steps=result["steps"]
    )
@app.post("/mcp/invoke",response_model = ToolInvokeResponse)
def invoke_tool(request: ToolInvokeRequest):
    result = mcp_gateway.invoke_tool(
        agent_id = request.agent_id,
        tool_name = request.tool_name,
        tool_input = request.tool_input
        
    )
    return ToolInvokeResponse(
        status=result["status"],
        error=result["error"],
        result=result["result"]
        
    )