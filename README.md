# Student-Focused Lowest Price Ride Optimization

A backend API project for finding affordable ride options for students.
The system is designed to recommend the lowest-price ride option based on user input.

## Project Overview

This project is a student-focused ride optimization system inspired by ride-booking platforms.
The goal is to help students find cheaper ride options by using price comparison and optimization logic.

## Features

* FastAPI backend
* Basic API health check
* Chat-based request handling
* AI planner agent structure
* Student-focused ride price optimization logic
* GitHub-ready project structure

## Tech Stack

* Python
* FastAPI
* Uvicorn
* Pydantic

## Project Structure

```text
student-focused-lowest-price-ride-optimization/
│
├── app/
│   ├── main.py
│   └── schemas.py
│
├── agents/
│   └── planner_agent.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## API Endpoints

### Health Check

```http
GET /
```

Response:

```json
{
  "message": "Student-focused ride optimization API is running.",
  "docs": "Go to /docs to test the API."
}
```

### Chat Endpoint

```http
POST /chat
```

Request body:

```json
{
  "user_id": "student_1",
  "message": "Find me the cheapest ride"
}
```

Response:

```json
{
  "user_id": "student_1",
  "answer": "I will help you find the lowest-price ride option.",
  "route": "price_optimization",
  "steps": [
    "Understand pickup and destination",
    "Compare available ride options",
    "Apply student-focused optimization",
    "Return the cheapest recommended ride"
  ]
}
```

## Installation

Create a virtual environment:

```bash
python -m venv .uber
```

Activate the virtual environment:

```bash
.uber\Scripts\activate
```

Install dependencies:

```bash
pip install fastapi uvicorn pydantic
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## GitHub Repository

```text
https://github.com/bonidarahas/student-focused-lowest-price-ride-optimization.git
```

## Current Status

The project currently includes the backend setup, API planning, schema structure, and AI planner agent direction.

## Future Improvements

* Add ride price comparison logic
* Add pickup and destination input
* Add student discount logic
* Add database support
* Add frontend interface
* Add real ride API integration
* Deploy the backend API
