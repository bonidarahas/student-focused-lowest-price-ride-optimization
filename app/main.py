from fastapi import FastAPI

from app.schemas import (
    ChatRequest,
    ChatResponse,
    ToolInvokeRequest,
    ToolInvokeResponse,
    RAGSearchRequest,
    SQLQueryRequest,
)

from agents.planner_agent import PlannerAgent
from agents.sql_agent import SQLAgent

from app.mcp_gateway import MCPGateway
from app.logger import AgentLogger
from app.event_bus import EventBus

from rag.vector_store import VectorStore
from evaluation.evaluator import AgentEvaluator


app = FastAPI(
    title="AgentMesh Lite",
    description="Mini Uber-style AI Agent Platform",
    version="0.9.0"
)


# Global service objects
planner_agent = PlannerAgent()
mcp_gateway = MCPGateway()
sql_agent = SQLAgent()
agent_logger = AgentLogger()
agent_evaluator = AgentEvaluator()
event_bus = EventBus()


@app.get("/")
def home():
    return {
        "message": "AgentMesh Lite is running.",
        "docs": "Go to /docs to test the API.",
        "version": "0.9.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Publish request event
    event_bus.publish(
        topic="agent.requests",
        event_type="chat_request_received",
        payload={
            "user_id": request.user_id,
            "message": request.message
        }
    )

    # Run planner agent
    result = planner_agent.handle_message(request.message)

    # Save agent steps to audit log table
    agent_logger.log_steps(
        user_id=request.user_id,
        route=result["route"],
        steps=result["steps"]
    )

    # Publish response event
    event_bus.publish(
        topic="agent.responses",
        event_type="chat_response_generated",
        payload={
            "user_id": request.user_id,
            "route": result["route"],
            "answer": result["answer"]
        }
    )

    # Publish every step as audit event
    for step in result["steps"]:
        event_bus.publish(
            topic="audit.logs",
            event_type="agent_step_completed",
            payload={
                "user_id": request.user_id,
                "route": result["route"],
                "agent": step.get("agent"),
                "action": step.get("action"),
                "details": step.get("details")
            }
        )

    return ChatResponse(
        user_id=request.user_id,
        answer=result["answer"],
        route=result["route"],
        steps=result["steps"]
    )


@app.post("/mcp/invoke", response_model=ToolInvokeResponse)
def invoke_tool(request: ToolInvokeRequest):
    result = mcp_gateway.invoke_tool(
        agent_id=request.agent_id,
        tool_name=request.tool_name,
        tool_input=request.tool_input
    )

    return ToolInvokeResponse(
        status=result["status"],
        result=result["result"],
        error=result["error"]
    )


@app.get("/rag/count")
def rag_count():
    vector_store = VectorStore()

    return {
        "collection": "uber_replica_docs",
        "count": vector_store.count()
    }


@app.post("/rag/search")
def rag_search(request: RAGSearchRequest):
    vector_store = VectorStore()

    results = vector_store.search(
        query=request.query,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "top_k": request.top_k,
        "results": results
    }


@app.post("/sql/query")
def sql_query(request: SQLQueryRequest):
    result = sql_agent.answer_question(request.question)

    return {
        "question": request.question,
        "answer": result["answer"],
        "sql": result["sql"],
        "rows": result["rows"]
    }


@app.get("/logs")
def get_logs(limit: int = 50):
    logs = agent_logger.get_logs(limit=limit)

    return {
        "count": len(logs),
        "logs": logs
    }


@app.get("/events")
def get_events(limit: int = 50):
    events = event_bus.get_events(limit=limit)

    return {
        "count": len(events),
        "events": events
    }


@app.get("/eval/run")
def run_evaluation():
    result = agent_evaluator.run_evaluation()
    return result


@app.get("/route/debug")
def debug_route(message: str):
    result = planner_agent.handle_message(message)

    return {
        "message": message,
        "route": result["route"],
        "answer": result["answer"],
        "steps": result["steps"]
    }