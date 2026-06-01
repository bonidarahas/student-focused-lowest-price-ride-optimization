import chromadb
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(
        self,
        collection_name: str = "uber_replica_docs",
        persist_path: str = "chroma_db"
    ):
        self.client = chromadb.PersistentClient(path=persist_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def add_documents(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        ids = []
        texts = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            ids.append(chunk["id"])
            texts.append(chunk["text"])
            metadatas.append({
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"]
            })

        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        search_results = []

        for doc, metadata, distance in zip(documents, metadatas, distances):
            search_results.append({
                "text": doc,
                "source": metadata.get("source"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": distance
            })

        return search_results

    def count(self) -> int:
        return self.collection.count()