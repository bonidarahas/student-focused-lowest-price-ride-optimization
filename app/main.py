from fastapi import FastAPI
from app.schemas import (ChatRequest, ChatResponse,ToolInvokeRequest , ToolInvokeResponse , SQLQueryRequest)
from agents.planner_agent import PlannerAgent
from app.mcp_gateway import MCPGateway
from rag.vector_store import VectorStore
from app.schemas import RAGSearchRequest
from agents.sql_agent import SQLAgent

app = FastAPI(
    title="AgentMesh Lite",
    description="Mini Uber-style AI Agent Platform",
    version="0.2.0"
)

planner_agent = PlannerAgent()
mcp_gateway = MCPGateway()
sql_agent = SQLAgent()



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
@app.get("/rag/count")
def rag_count():
    vector_store = VectorStore()

    return{
        "collection": "uber_replica_docs",
        "count": vector_store.count()
    }

@app.post("/rag/search")
def rag_search(request: RAGSearchRequest):
    vector_store = VectorStore()

    results = vector_store.search(
        query= request.query,
        top_k = request.top_k

    )

    return{
        "query": request.query,
        "top_k" : request.top_k,
        "results":results

    }
@app.post("/sql/query")
def sql_query(request: SQLQueryRequest):
    result = sql_agent.answer_question(request.question)

    return{
        "question": request.question,
        "answer": result ["sql"],
        "sql": result["sql"],
        "rows":result["rows"]


    }