from rag.embeddings import create_embeddings

from rag.vector_store import load_vector_store


def search_document(
    user_id,
    document_id,
    question,
    top_k=5
):

    index, metadata = load_vector_store(
        user_id,
        document_id
    )

    if index is None:

        raise ValueError(
            "Vector index not found for this document."
        )


    if not metadata:

        return []


    question_embedding = create_embeddings(
        [question]
    )


    scores, indices = index.search(
        question_embedding,
        min(top_k, index.ntotal)
    )


    results = []


    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id < 0:
            continue


        chunk = metadata[index_id]


        results.append({

            "chunk_id":
            chunk["chunk_id"],

            "text":
            chunk["text"],

            "score":
            float(score)

        })


    return results