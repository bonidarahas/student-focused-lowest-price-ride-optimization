EVAL_CASES = [
    {
        "id": 1,
        "question": "What is Kafka?",
        "expected_route": "general_answer"
    },
    {
        "id": 2,
        "question": "calculate 18 * 13.5",
        "expected_route": "calculator"
    },
    {
        "id": 3,
        "question": "What is the student discount policy?",
        "expected_route": "rag"
    },
    {
        "id": 4,
        "question": "How does cancellation work?",
        "expected_route": "rag"
    },
    {
        "id": 5,
        "question": "Do premium rides qualify for the student discount?",
        "expected_route": "rag"
    },
    {
        "id": 6,
        "question": "How are drivers matched?",
        "expected_route": "rag"
    },
    {
        "id": 7,
        "question": "Which driver earned the most?",
        "expected_route": "sql"
    },
    {
        "id": 8,
        "question": "What is total revenue?",
        "expected_route": "sql"
    },
    {
        "id": 9,
        "question": "How many student rides are there?",
        "expected_route": "sql"
    },
    {
        "id": 10,
        "question": "What is the average fare?",
        "expected_route": "sql"
    },
    {
        "id": 11,
        "question": "Show the top drivers by earnings",
        "expected_route": "sql"
    },
    {
        "id": 12,
        "question": "Book me a student ride from Hamilton to Hudson",
        "expected_route": "ride_booking"
    },
    {
        "id": 13,
        "question": "Book ride from Newark Penn Station to NJIT",
        "expected_route": "ride_booking"
    },
    {
        "id": 14,
        "question": "I need a ride from Bridgeport Station to University of Bridgeport",
        "expected_route": "ride_booking"
    },
    {
        "id": 15,
        "question": "Get me a ride from Hoboken to Jersey City",
        "expected_route": "ride_booking"
    },
    {
        "id": 16,
        "question": "Schedule a student ride from NJIT to Newark Airport",
        "expected_route": "ride_booking"
    },
    {
        "id": 17,
        "question": "calculate (25 + 5) * 3",
        "expected_route": "calculator"
    },
    {
        "id": 18,
        "question": "solve 100 / 4",
        "expected_route": "calculator"
    },
    {
        "id": 19,
        "question": "Explain what an AI agent is",
        "expected_route": "general_answer"
    },
    {
        "id": 20,
        "question": "What is RAG?",
        "expected_route": "general_answer"
    }
]