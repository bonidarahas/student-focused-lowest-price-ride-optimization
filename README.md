# Student-Focused Lowest Price Ride Optimization

A FastAPI-based Uber-inspired AI agent platform that combines multi-agent routing, RAG, SQL querying, Kafka event streaming, audit logging, and student-focused ride price optimization.

This project simulates how a modern ride-sharing backend could use AI agents and event-driven architecture to answer user questions, search policy documents, query ride data, calculate prices, and book the lowest-price ride for students.

---

## Project Overview

This project started as an Uber replica backend and evolved into a production-style AI agent platform.

The system can:

* Route user messages through a Planner Agent
* Answer general AI/system questions through an AI Gateway
* Use an MCP-style Tool Gateway for tool execution
* Search ride policy documents using RAG and ChromaDB
* Query ride, driver, and payment data using a SQL Agent
* Log agent actions into SQLite
* Publish events to a Kafka-style event bus
* Integrate with real Apache Kafka using Docker
* Simulate student-focused ride price optimization
* Book rides through natural language chat

---

## Current Features

### 1. Planner Agent

The Planner Agent receives the user message and decides which route should handle it.

Supported routes:

```text
general_answer
calculator
rag
sql
ride_booking
```

Example:

```json
{
  "user_id": "Boni",
  "message": "Which driver earned the most?"
}
```

Route:

```text
sql
```

---

### 2. AI Gateway

The AI Gateway centralizes model-style responses.

Current version uses a simple mock response layer. It can later be replaced with:

* OpenAI
* Ollama
* Claude
* Groq
* Local LLMs

---

### 3. MCP-Style Tool Gateway

The MCP Gateway controls tool access.

Instead of agents directly calling tools, they call the gateway first.

Example:

```text
Planner Agent → MCP Gateway → Calculator Tool
```

This adds a production-style permission layer.

Supported tool:

```text
calculator
```

Example request:

```json
{
  "agent_id": "planner_agent",
  "tool_name": "calculator",
  "tool_input": {
    "expression": "18 * 13.5"
  }
}
```

---

### 4. RAG Agent with ChromaDB

The RAG Agent searches local policy documents using embeddings and ChromaDB.

RAG pipeline:

```text
policy documents
→ text chunks
→ embeddings
→ ChromaDB
→ semantic search
→ answer
```

Useful for policy questions such as:

```text
What is the student discount policy?
How does cancellation work?
Do premium rides qualify for student discounts?
```

---

### 5. SQL Agent

The SQL Agent queries ride data stored in SQLite.

Database tables:

```text
drivers
rides
payments
ride_bookings
agent_logs
events
processed_events
```

Example questions:

```text
Which driver earned the most?
What is total revenue?
How many student rides are there?
What is the average fare?
```

---

### 6. Agent Logging and Audit Trail

Every `/chat` request stores agent steps in the database.

Example logged actions:

```text
received_message
selected_route
executed_sql_query
searched_documents
created_ride_booking
generated_response
```

Endpoint:

```text
GET /logs
```

---

### 7. Kafka-Style Event Bus

The project includes a local event bus simulation using SQLite.

Event topics include:

```text
agent.requests
agent.responses
audit.logs
ride.bookings
```

Endpoint:

```text
GET /events
```

---

### 8. Real Apache Kafka Integration

The project also includes real Kafka integration using Docker Compose.

Kafka is used to publish agent and ride events.

Kafka files:

```text
docker-compose.yml
kafka_service/
  producer.py
  consumer.py
  worker.py
```

Kafka topics:

```text
agent.requests
agent.responses
audit.logs
ride.bookings
```

---

### 9. Kafka Background Worker

The Kafka background worker consumes events and stores processed events in SQLite.

Run worker:

```bash
python -m kafka_service.worker
```

View processed events:

```text
GET /worker/events
```

---

### 10. Student Ride Price Optimization

The core business feature is student-focused lowest-price ride optimization.

The system:

1. Finds available drivers
2. Estimates ride prices
3. Applies a student discount when eligible
4. Selects the lowest final price
5. Creates a simulated ride booking

Example direct endpoint:

```text
POST /rides/estimate
```

Example request:

```json
{
  "rider_name": "Boni",
  "pickup_location": "Hamilton",
  "dropoff_location": "Hudson",
  "is_student": true
}
```

Example response:

```json
{
  "rider_name": "Boni",
  "pickup_location": "Hamilton",
  "dropoff_location": "Hudson",
  "is_student": true,
  "selected_option": {
    "driver_id": 2,
    "driver_name": "Maria Lopez",
    "rating": 4.7,
    "estimated_pickup_minutes": 5,
    "base_price": 11.75,
    "discount_amount": 1.76,
    "final_price": 9.99
  },
  "reason": "Lowest final price selected after applying verified student discount."
}
```

---

### 11. Natural Language Ride Booking

Users can book rides through `/chat`.

Example:

```json
{
  "user_id": "Boni",
  "message": "Book me a student ride from Hamilton to Hudson"
}
```

Expected route:

```text
ride_booking
```

Example answer:

```text
Ride booked successfully. Driver: Maria Lopez. Final price: $9.99. Status: confirmed.
```

---

## Architecture

```text
User
 ↓
FastAPI API
 ↓
Planner Agent
 ├── AI Gateway
 ├── MCP Tool Gateway → Calculator Tool
 ├── RAG Agent → ChromaDB
 ├── SQL Agent → SQLite
 └── Ride Booking Service → Pricing Service → SQLite
 ↓
Agent Logger → agent_logs table
 ↓
Event Bus → events table
 ↓
Kafka Producer → Apache Kafka
 ↓
Kafka Worker → processed_events table
```

---

## Tech Stack

* Python
* FastAPI
* Pydantic
* SQLite
* ChromaDB
* Sentence Transformers
* Apache Kafka
* Docker Compose
* Confluent Kafka Python Client
* Uvicorn

---

## Project Structure

```text
Uber_replica/
  app/
    main.py
    schemas.py
    ride_schemas.py
    ai_gateway.py
    mcp_gateway.py
    logger.py
    event_bus.py

  agents/
    planner_agent.py
    rag_agent.py
    sql_agent.py

  services/
    pricing_service.py
    ride_booking_service.py

  tools/
    calculator.py

  rag/
    document_loader.py
    text_splitter.py
    vector_store.py
    index_documents.py

  database/
    setup_db.py

  evaluation/
    eval_cases.py
    evaluator.py

  kafka_service/
    producer.py
    consumer.py
    worker.py

  data/
    docs/
      policy.txt

  docker-compose.yml
  requirements.txt
  README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/bonidarahas/student-focused-lowest-price-ride-optimization.git
cd student-focused-lowest-price-ride-optimization
```

---

### 2. Create and Activate Virtual Environment

Windows PowerShell:

```powershell
python -m venv .uber
.uber\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create SQLite Database

```bash
python -m database.setup_db
```

This creates:

```text
database/uber_replica.db
```

---

### 5. Index RAG Documents

```bash
python -m rag.index_documents
```

This creates local ChromaDB embeddings.

---

### 6. Start Kafka with Docker

```bash
docker compose up -d
```

Check Kafka:

```bash
docker compose ps
```

---

### 7. Start FastAPI

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Health Check

```text
GET /
```

---

### Chat Agent

```text
POST /chat
```

Example:

```json
{
  "user_id": "Boni",
  "message": "Book me a student ride from Hamilton to Hudson"
}
```

---

### MCP Tool Invocation

```text
POST /mcp/invoke
```

Example:

```json
{
  "agent_id": "planner_agent",
  "tool_name": "calculator",
  "tool_input": {
    "expression": "18 * 13.5"
  }
}
```

---

### RAG Count

```text
GET /rag/count
```

---

### RAG Search

```text
POST /rag/search
```

Example:

```json
{
  "query": "student discount",
  "top_k": 3
}
```

---

### SQL Query

```text
POST /sql/query
```

Example:

```json
{
  "question": "Which driver earned the most?"
}
```

---

### Ride Estimate

```text
POST /rides/estimate
```

Example:

```json
{
  "rider_name": "Boni",
  "pickup_location": "Hamilton",
  "dropoff_location": "Hudson",
  "is_student": true
}
```

---

### Book Ride

```text
POST /rides/book
```

Example:

```json
{
  "rider_name": "Boni",
  "pickup_location": "Hamilton",
  "dropoff_location": "Hudson",
  "is_student": true
}
```

---

### List Ride Bookings

```text
GET /rides
```

---

### Logs

```text
GET /logs
```

---

### Events

```text
GET /events
```

---

### Worker Processed Events

```text
GET /worker/events
```

---

### Evaluation

```text
GET /eval/run
```

---

### Route Debug

```text
GET /route/debug?message=Book me a student ride from Hamilton to Hudson
```

---

## Kafka Commands

Start Kafka:

```bash
docker compose up -d
```

Stop Kafka:

```bash
docker compose down
```

Check Kafka logs:

```bash
docker compose logs -f kafka
```

Run Kafka consumer:

```bash
python -m kafka_service.consumer
```

Run Kafka worker:

```bash
python -m kafka_service.worker
```

---

## Example Test Flow

### 1. Start the API

```bash
uvicorn app.main:app --reload
```

### 2. Test ride booking through chat

```json
{
  "user_id": "Boni",
  "message": "Book me a student ride from Hamilton to Hudson"
}
```

Expected:

```text
route: ride_booking
status: confirmed
student discount applied
```

### 3. Check saved rides

```text
GET /rides
```

### 4. Check agent logs

```text
GET /logs
```

### 5. Check events

```text
GET /events
```

---

## Evaluation System

The project includes route evaluation for the Planner Agent.

Run:

```text
GET /eval/run
```

Example test cases:

```text
What is Kafka? → general_answer
calculate 18 * 13.5 → calculator
What is the student discount policy? → rag
Which driver earned the most? → sql
Book me a student ride from Hamilton to Hudson → ride_booking
```

---

## Completed Milestones

### Milestone 1: FastAPI + Planner Agent

* Added `/chat`
* Added Planner Agent
* Added AI Gateway

### Milestone 2: MCP-Style Tool Gateway

* Added calculator tool
* Added permission-based tool gateway
* Added `/mcp/invoke`

### Milestone 3: Basic RAG Agent

* Added document-based policy answering

### Milestone 4: Real RAG with ChromaDB

* Added embeddings
* Added ChromaDB vector store
* Added document indexing
* Added `/rag/count` and `/rag/search`

### Milestone 5: SQL Agent

* Added SQLite database
* Added driver, ride, and payment data
* Added SQL Agent
* Added `/sql/query`

### Milestone 6: Event Logging + Audit Trail

* Added `agent_logs`
* Added `/logs`

### Milestone 7: Evaluation System

* Added evaluation cases
* Added `/eval/run`

### Milestone 8: Improved Planner Routing

* Improved route detection for RAG, SQL, calculator, and ride booking

### Milestone 9: Kafka-Style Event Bus Simulation

* Added local SQLite event bus
* Added `/events`

### Milestone 10: Real Kafka Integration

* Added Docker Compose Kafka setup
* Added Kafka producer and consumer

### Milestone 11: Kafka Background Worker

* Added background worker
* Added processed event tracking
* Added `/worker/events`

### Milestone 12: Student Price Optimization + Ride Booking

* Added pricing service
* Added ride booking service
* Added `/rides/estimate`, `/rides/book`, and `/rides`

### Milestone 13: Natural Language Ride Booking

* Connected ride booking to Planner Agent
* Enabled `/chat` to book rides

### Milestone 14: Deterministic Pricing + Improved Ride Parser

* Removed random pricing behavior
* Added stable deterministic pricing
* Improved natural language ride parsing

---

## Resume-Ready Summary

Built a production-style AI agent platform for a student-focused Uber replica using FastAPI, ChromaDB, SQLite, Apache Kafka, and Docker. Implemented a Planner Agent with multi-route decision logic, MCP-style tool gateway, RAG document search, SQL querying, audit logging, event streaming, Kafka background workers, and a deterministic student ride price optimization engine with natural-language ride booking.

---

## Future Improvements

* Add user authentication
* Add real student email verification
* Add real map/distance API
* Add frontend UI
* Add real LLM integration with OpenAI or Ollama
* Add payment simulation
* Add driver availability status
* Add pricing experiments
* Add deployment with Dockerized FastAPI
* Add monitoring dashboard

---

## Repository

```text
https://github.com/bonidarahas/student-focused-lowest-price-ride-optimization
```
