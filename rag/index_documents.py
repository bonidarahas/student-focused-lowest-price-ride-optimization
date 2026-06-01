from rag.document_loader import load_txt_documents
from rag.text_splitter import split_text
from rag.vector_store import VectorStore


def index_documents():
    documents = load_txt_documents("data/docs")
    chunks = []

    for doc in documents:
        text_chunks = split_text(doc["text"])
        for index , chunk_text in enumerate(text_chunks):
            chunks.append({
                "id":f"{doc['source']}+{index}",
                "source" : doc["source"],
                "chunk_index": index,
                "text": chunk_text
            })
        vector_store = VectorStore()
        vector_store.add_documents(chunks)

        print(f"loaded documents: {len(documents)}")
        print(f"Indexed chunks: {len(chunks)}")
        print(f"Vector DB count: {vector_store.count()}")


if __name__=="__main__":
    index_documents()
