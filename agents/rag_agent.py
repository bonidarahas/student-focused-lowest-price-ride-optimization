from pathlib import Path

class RAGAgent:

    """
    Simple rag agent 
    
    need to be upgraded"""

    def __init__(self , docs_folder: str = "data/docs"):
        self.docs_folder = Path(docs_folder)

    def answer_question(self, question:str) -> dict:
        documents  = self._load_documents()

        if not documents:
            return{
                "answer" : "i couldnot find any documents in the knowledge base",
                "sources":[]

            }
        best_doc = self._search_documents(question,documents)

        if best_doc is None:
            return{

                "answer": "i couldnot find any relevant information in the documents",
                "sources":[]
                
            }

        answer = self._generate_answer(question, best_doc["text"])
        return{
            "answer": answer,
            "sources": [best_doc["source"]]
        }
    
    def _load_documents(self) -> list:
        documents = []

        for file_path in self.docs_folder.glob("+.txt"):
            text = file_path.read_text(encoding= "utf-8")

            documents.append({
                "sources": file_path.name,
                "text": text
            })
            return documents
        
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