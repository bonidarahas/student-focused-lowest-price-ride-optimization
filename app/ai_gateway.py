class AIGateway:
    """
    Central place for all model calls """   


    def generate_response(self , prompt: str) -> str:
        prompt_lower = prompt.lower()

        if"ai_agent" in prompt_lower:
            return(
                "An AI agent is a software that can understand a goal , reason about what to do ,"
                "use tools if needed , and return a result . In Production systems , agents often"
                "work with apis , databases , search toolls , and permission systems ."
            )
        
        if "rag" in prompt_lower:
            return(
                "Rag stands for Retrieval Augmented Generation . It is a technique that combines retrieval of relevant information with generation of natural language responses . RAG models can access external knowledge sources to provide more accurate and up-to-date answers ."
            )
        
        if "kafka" in prompt_lower:
            return(
                "Kafka is a distributed streaming platform that can be used for building real-time data pipelines and streaming applications . It is designed to handle high-throughput , fault-tolerant , and scalable data streams . Kafka can be used for various use cases such as log aggregation , event sourcing , and stream processing ."
            )
        # Placeholder for actual model call
        return f"Generated response for: {prompt}"