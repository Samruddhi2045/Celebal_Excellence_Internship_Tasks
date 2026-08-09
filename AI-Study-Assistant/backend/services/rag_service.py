from rag.chunker import create_chunks

from rag.embeddings import create_embeddings

from rag.vector_store import (
    create_vector_store
)


def index_document(
    user_id,
    document_id,
    text
):

    # Step 1: Chunk
    chunks = create_chunks(
        text
    )


    if not chunks:

        raise ValueError(
            "Document does not contain enough readable text."
        )


    # Step 2: Embeddings
    embeddings = create_embeddings(
        chunks
    )


    # Step 3: FAISS
    result = create_vector_store(
        user_id,
        document_id,
        chunks,
        embeddings
    )


    return {
        "chunks": len(chunks),
        "vector_store": result
    }