from pathlib import Path


def load_txt_documents(folder_path: str = "data/docs") -> list[dict]:
    folder = Path(folder_path)
    documents = []

    if not folder.exists():
        return documents

    for file_path in folder.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents