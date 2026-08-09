def clean_text(text):
    """
    Clean extracted document text.
    """

    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    lines = []

    for line in text.split("\n"):

        line = " ".join(
            line.split()
        )

        if line:
            lines.append(line)

    return "\n".join(lines)


def create_chunks(
    text,
    chunk_size=800,
    overlap=150
):
    """
    Split document text into overlapping chunks.

    chunk_size:
        Approximate number of characters per chunk.

    overlap:
        Number of characters shared between chunks.
    """

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():

            chunks.append(
                chunk.strip()
            )

        if end >= text_length:
            break

        start = end - overlap

    return chunks