from rag.vector_store import VectorStore

class RAGAgent:
    def __init__(self):
        self.vector_store= VectorStore()

        def answer_question(self, question:str) -> dict:
            results =self.vector_store.search(query=question, top_k =3)

            if not results:
                return{
                    "answer": "I couldnot find the info from the knowledge base",
                    "sources": []

                }
            
            context = "\n\n".join(
                [result["text"] for result in results]
            )
            sources = list(
                set([result["source"] for result in results])

            )
            answer = self._generate_answer(question,context)

            return{
                "answer": answer ,
                "sources": sources
            }

    def _generate_answer(self , question:str , context:str) -> str:
        question_lower = question.lower()
        context_lower = context.lower()

        if "student" in question_lower and "discount" in question_lower:
            return ("students are eligible for  a 15percent discount except for the premium rides"
            )
        if "cancel" in question_lower or "cancellation" in question_lower:
            return(
                "Ride cancellation is free until 2 minutes after booking",
                "after 2 mins the fee may be applied."
            )
        if "driver" in question_lower or "match" in question_lower:
            return(
                " Drivers are matched based on distance , rating ,availability,"
                " and estimated picup time."

            )
        if "lowest" in question_lower or "price" in question_lower:
            return (
                "for verified studentrs , the system compares prices from nearby drivers,"
                " and tries to assign available lowest price for the ride"
            )
        return(
            "i found relevant info in the documents but this is simple rag with out the embeddings "
            "wait for the next updates to get better answers " \
            "context: " + context[:300]
        )