def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Splits long text into smaller overlapping chunks.

    Example:
    chunk 1: characters 0-500
    chunk 2: characters 400-900
    chunk 3: characters 800-1300
    """

    chunks = []

    if not text:
        return chunks

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks