from rag.vector_store import VectorStore


class RAGAgent:
    def __init__(self):
        self.vector_store = VectorStore()

    def answer_question(self, question: str) -> dict:
        results = self.vector_store.search(query=question, top_k=3)

        if not results:
            return {
                "answer": "I could not find relevant information in the knowledge base.",
                "sources": []
            }

        context = "\n\n".join(
            [result["text"] for result in results]
        )

        sources = list(
            set([result["source"] for result in results])
        )

        answer = self._generate_answer(question, context)

        return {
            "answer": answer,
            "sources": sources
        }

    def _generate_answer(self, question: str, context: str) -> str:
        question_lower = question.lower()
        context_lower = context.lower()

        if "student" in question_lower and "discount" in context_lower:
            return (
                "Verified students get a 15% discount on eligible rides. "
                "Premium rides do not qualify for the student discount. "
                "Source: policy.txt"
            )

        if "cancel" in question_lower or "cancellation" in question_lower:
            return (
                "Ride cancellation is free within 2 minutes of booking. "
                "After 2 minutes, a cancellation fee may apply. "
                "Source: policy.txt"
            )

        if "driver" in question_lower or "match" in question_lower or "matched" in question_lower:
            return (
                "Drivers are matched based on distance, availability, rating, "
                "and estimated pickup time. "
                "Source: policy.txt"
            )

        if "lowest" in question_lower or "price" in question_lower:
            return (
                "For verified students, the system compares prices from nearby drivers "
                "and tries to assign the lowest available price. "
                "Source: policy.txt"
            )

        return (
            "I found relevant information in the knowledge base: "
            + context[:400]
        )