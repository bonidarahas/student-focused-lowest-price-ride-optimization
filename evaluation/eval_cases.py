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
        "question": "Which driver earned the most?",
        "expected_route": "sql"
    },
    {
        "id": 6,
        "question": "What is total revenue?",
        "expected_route": "sql"
    },
    {
        "id": 7,
        "question": "How many student rides are there?",
        "expected_route": "sql"
    },
    {
        "id": 8,
        "question": "What is the average fare?",
        "expected_route": "sql"
    }
    {
        "id": 9,
        "question": "Book me a ride from hudson park to 753 Hamilton street"
        "expected_route": "ride-booking"
    }
]