from pydantic import BaseModel
from typing import Any, Dict, Optional , List , Literal


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

class RideEstimateRequest(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    is_student: bool = False

class DriverPriceOption(BaseModel):
    driver_id: int
    driver_name: str
    rating: float
    estimated_pickup_minutes: int
    base_price: float
    discount_amount: float
    final_price : float
class RideEstimateResponse(BaseModel):
    rider_name: str
    pickup_loation : str
    dropoff_locatiohn: str
    is_student: bool
    selected_option :  DriverPriceOption
    all_option : List[DriverPriceOption]
    reason: str

class RideBookingRequest(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    is_student : bool = False

class RideBookingResponse(BaseModel):
    booking_id : int
    rider_namer: str
    driver_id : int 
    driver_name: str
    pickup_location: str
    dropff_location : str
    final_price: float 
    status : str
    reason : str 




class RideStatusUpdateRequest(BaseModel):
    status:Literal[
        "confirmed",
        "driver_arriving",
        "in_progress",
        "completed",
        "cancelled"
    ]
class RideStatusUpdateResponse(BaseModel):
    booking_id:int
    rider_name:str
    driver_name:str
    previous_status:str
    new_status:str
    message:str



