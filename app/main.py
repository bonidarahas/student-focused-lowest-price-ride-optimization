import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI

from app.schemas import (
    ChatRequest,
    ChatResponse,
    ToolInvokeRequest,
    ToolInvokeResponse,
    RAGSearchRequest,
    SQLQueryRequest,
)

from app.ride_schemas import (
    RideEstimateRequest,
    RideEstimateResponse,
    RideBookingRequest,
    RideBookingResponse,
)

from agents.planner_agent import PlannerAgent
from agents.sql_agent import SQLAgent

from app.mcp_gateway import MCPGateway
from app.logger import AgentLogger
from app.event_bus import EventBus

from rag.vector_store import VectorStore
from evaluation.evaluator import AgentEvaluator

from kafka_service.producer import KafkaEventProducer
from services.ride_booking_service import RideBookingService


app = FastAPI(
    title="AgentMesh Lite",
    description="Mini Uber-style AI Agent Platform with Student Ride Optimization",
    version="0.12.0"
)


# Global service objects
planner_agent = PlannerAgent()
mcp_gateway = MCPGateway()
sql_agent = SQLAgent()
agent_logger = AgentLogger()
agent_evaluator = AgentEvaluator()
event_bus = EventBus()
kafka_producer = KafkaEventProducer()
ride_booking_service = RideBookingService()


@app.get("/")
def home():
    return {
        "message": "AgentMesh Lite is running.",
        "docs": "Go to /docs to test the API.",
        "version": "0.12.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # 1. Save request event locally
    event_bus.publish(
        topic="agent.requests",
        event_type="chat_request_received",
        payload={
            "user_id": request.user_id,
            "message": request.message
        }
    )

    # 2. Publish request event to Kafka
    try:
        kafka_producer.publish(
            topic="agent.requests",
            event_type="chat_request_received",
            payload={
                "user_id": request.user_id,
                "message": request.message
            }
        )
    except Exception as error:
        print(f"Kafka request publish failed: {error}")

    # 3. Run planner agent
    result = planner_agent.handle_message(request.message)

    # 4. Save agent steps to SQLite logs
    agent_logger.log_steps(
        user_id=request.user_id,
        route=result["route"],
        steps=result["steps"]
    )

    # 5. Save response event locally
    event_bus.publish(
        topic="agent.responses",
        event_type="chat_response_generated",
        payload={
            "user_id": request.user_id,
            "route": result["route"],
            "answer": result["answer"]
        }
    )

    # 6. Publish response event to Kafka
    try:
        kafka_producer.publish(
            topic="agent.responses",
            event_type="chat_response_generated",
            payload={
                "user_id": request.user_id,
                "route": result["route"],
                "answer": result["answer"]
            }
        )
    except Exception as error:
        print(f"Kafka response publish failed: {error}")

    # 7. Save and publish every agent step
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

        try:
            kafka_producer.publish(
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
        except Exception as error:
            print(f"Kafka audit publish failed: {error}")

    try:
        kafka_producer.flush()
    except Exception as error:
        print(f"Kafka flush failed: {error}")

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


@app.post("/rides/estimate", response_model=RideEstimateResponse)
def estimate_ride(request: RideEstimateRequest):
    result = ride_booking_service.estimate_ride(
        rider_name=request.rider_name,
        pickup_location=request.pickup_location,
        dropoff_location=request.dropoff_location,
        is_student=request.is_student
    )

    return RideEstimateResponse(
        rider_name=request.rider_name,
        pickup_location=request.pickup_location,
        dropoff_location=request.dropoff_location,
        is_student=request.is_student,
        selected_option=result["selected_option"],
        all_options=result["all_options"],
        reason=result["reason"]
    )


@app.post("/rides/book", response_model=RideBookingResponse)
def book_ride(request: RideBookingRequest):
    result = ride_booking_service.book_ride(
        rider_name=request.rider_name,
        pickup_location=request.pickup_location,
        dropoff_location=request.dropoff_location,
        is_student=request.is_student
    )

    event_bus.publish(
        topic="ride.bookings",
        event_type="ride_booking_created",
        payload=result
    )

    try:
        kafka_producer.publish(
            topic="ride.bookings",
            event_type="ride_booking_created",
            payload=result
        )
        kafka_producer.flush()
    except Exception as error:
        print(f"Kafka ride booking publish failed: {error}")

    return RideBookingResponse(
        booking_id=result["booking_id"],
        rider_name=result["rider_name"],
        driver_id=result["driver_id"],
        driver_name=result["driver_name"],
        pickup_location=result["pickup_location"],
        dropoff_location=result["dropoff_location"],
        final_price=result["final_price"],
        status=result["status"],
        reason=result["reason"]
    )


@app.get("/rides")
def list_rides(limit: int = 50):
    bookings = ride_booking_service.list_bookings(limit=limit)

    return {
        "count": len(bookings),
        "bookings": bookings
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


@app.get("/worker/events")
def get_processed_events(limit: int = 50):
    db_path = Path("database/uber_replica.db")

    if not db_path.exists():
        return {
            "count": 0,
            "events": [],
            "message": "Database does not exist."
        }

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            processed_id,
            topic,
            event_type,
            payload,
            kafka_partition,
            kafka_offset,
            processed_at
        FROM processed_events
        ORDER BY processed_id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    events = []

    for row in rows:
        events.append({
            "processed_id": row[0],
            "topic": row[1],
            "event_type": row[2],
            "payload": json.loads(row[3]),
            "partition": row[4],
            "offset": row[5],
            "processed_at": row[6]
        })

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