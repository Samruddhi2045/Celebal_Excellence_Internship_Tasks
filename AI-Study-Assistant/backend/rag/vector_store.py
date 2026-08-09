import os
import json

import faiss
import numpy as np


VECTOR_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "vector_store"
)


def get_document_folder(
    user_id,
    document_id
):

    folder = os.path.join(
        VECTOR_FOLDER,
        f"user_{user_id}",
        f"document_{document_id}"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


def create_vector_store(
    user_id,
    document_id,
    chunks,
    embeddings
):

    folder = get_document_folder(
        user_id,
        document_id
    )


    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )


    dimension = embeddings.shape[1]


    index = faiss.IndexFlatIP(
        dimension
    )


    index.add(
        embeddings
    )


    index_path = os.path.join(
        folder,
        "index.faiss"
    )


    metadata_path = os.path.join(
        folder,
        "chunks.json"
    )


    faiss.write_index(
        index,
        index_path
    )


    metadata = [

        {
            "chunk_id": index,
            "text": chunk
        }

        for index, chunk
        in enumerate(chunks)

    ]


    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )


    return {
        "index_path": index_path,
        "metadata_path": metadata_path,
        "chunks": len(chunks)
    }


def load_vector_store(
    user_id,
    document_id
):

    folder = get_document_folder(
        user_id,
        document_id
    )


    index_path = os.path.join(
        folder,
        "index.faiss"
    )


    metadata_path = os.path.join(
        folder,
        "chunks.json"
    )


    if not os.path.exists(
        index_path
    ):

        return None, None


    if not os.path.exists(
        metadata_path
    ):

        return None, None


    index = faiss.read_index(
        index_path
    )


    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(
            file
        )


    return index, metadata