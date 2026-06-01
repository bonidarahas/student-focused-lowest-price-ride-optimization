from pydantic import BaseModel
from typing import Any, Dict, Optional , List


class ChatRequest(BaseModel):
    user_id: str
    message: str


class AgentStep(BaseModel):
    agent:str
    action:str
    details: Optional[str] = None

class ChatResponse(BaseModel):
    user_id:str
    answer:str
    route:str
    steps: List[AgentStep]

class ToolInvokeRequest(BaseModel):
    agent_id:str
    tool_name:str
    tool_input: Dict[str ,Any]


class ToolInvokeResponse(BaseModel):
    status:str
    error: Optional[str] = None
    result: Optional[Any] = None


class RAGSearchRequest(BaseModel):
    query: str
    top_k : int=3 


class SQLQueryRequest(BaseModel):
    question:str



