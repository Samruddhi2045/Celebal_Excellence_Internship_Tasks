import os

import faiss
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# CONFIGURATION
DOCUMENTS_FOLDER = "documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

#Gemini model
GEMINI_MODEL_NAME = "gemini-3.6-flash"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3

# ENVIRONMENT SETUP

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "\nGEMINI_API_KEY was not found.\n"
        "Create a .env file and add:\n\n"
        "GEMINI_API_KEY=your_api_key_here\n"
    )

# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)

# LOAD EMBEDDING MODEL

print("\nLoading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

print("Embedding model loaded successfully!")

# STEP 1: LOAD PDF

def load_pdf(file_path):
    """
    Extract text from a PDF file.
    """

    reader = PdfReader(file_path)

    full_text = ""

    for page_number, page in enumerate(reader.pages):

        try:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

        except Exception as error:

            print(
                f"Warning: Could not read page "
                f"{page_number + 1}: {error}"
            )

    return full_text

# STEP 2: TEXT CHUNKING

def split_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    """
    Split document text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# STEP 3: CREATE EMBEDDINGS

def create_embeddings(chunks):
    """
    Convert document chunks into vector embeddings.
    """

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")

    # Normalize embeddings so inner product behaves
    # like cosine similarity.
    faiss.normalize_L2(embeddings)

    return embeddings

# STEP 4: CREATE FAISS VECTOR DATABASE

def create_vector_store(embeddings):
    """
    Store embeddings in a FAISS index.

    IndexFlatIP + normalized embeddings =
    cosine similarity search.
    """

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    return index


# STEP 5: RETRIEVE RELEVANT CHUNKS

def retrieve_chunks(
    question,
    index,
    chunks,
    top_k=TOP_K
):
    """
    Retrieve chunks most relevant to the user's question.
    """

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    ).astype("float32")

    # Normalize question embedding
    faiss.normalize_L2(
        question_embedding
    )

    # Make sure top_k is not greater
    # than number of available chunks.
    top_k = min(
        top_k,
        len(chunks)
    )

    scores, indices = index.search(
        question_embedding,
        top_k
    )

    relevant_chunks = []

    for i in indices[0]:

        if 0 <= i < len(chunks):

            relevant_chunks.append(
                chunks[i]
            )

    return relevant_chunks

# STEP 6: GENERATE ANSWER USING GEMINI

def generate_answer(
    question,
    relevant_chunks
):
    """
    Generate an answer using only the retrieved document
    context.
    """

    context = "\n\n".join(
        relevant_chunks
    )

    prompt = f"""
You are a Document Question Answering Assistant.

Your task is to answer the user's question using ONLY
the information contained in the DOCUMENT CONTEXT.

IMPORTANT RULES:

1. Use only information from the provided context.

2. Do not use outside knowledge.

3. Do not invent information.

4. If the answer is not available in the context,
respond exactly:

"The information is not available in the provided document."

5. Give a clear and concise answer.

6. If multiple relevant pieces of information are present,
combine them into a well-structured answer.


DOCUMENT CONTEXT

{context}


USER QUESTION:

{question}


ANSWER:
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt
    )

    if response.text:

        return response.text.strip()

    return (
        "The information is not available "
        "in the provided document."
    )

# FIND PDF

def find_pdf():
    """
    Automatically find the first PDF inside
    the documents folder.
    """

    if not os.path.exists(
        DOCUMENTS_FOLDER
    ):

        os.makedirs(
            DOCUMENTS_FOLDER
        )

        print(
            "\nThe documents folder was created."
        )

        print(
            "Please place a PDF inside it."
        )

        return None

    pdf_files = [
        file
        for file in os.listdir(
            DOCUMENTS_FOLDER
        )
        if file.lower().endswith(".pdf")
    ]

    if not pdf_files:

        print(
            "\nNo PDF files found inside "
            "the documents folder."
        )

        print(
            "Please add a PDF and run "
            "the program again."
        )

        return None

    pdf_path = os.path.join(
        DOCUMENTS_FOLDER,
        pdf_files[0]
    )

    return pdf_path

# MAIN PROGRAM

if __name__ == "__main__":

    print(
        "   DOCUMENT QUESTION ANSWERING SYSTEM"
    )

    # FIND PDF

    pdf_path = find_pdf()

    if pdf_path is None:
        exit()


    print(
        "\nUsing PDF:"
    )

    print(
        pdf_path
    )


    # LOAD PDF

    print(
        "\n[1/4] Loading PDF..."
    )

    try:

        text = load_pdf(
            pdf_path
        )

    except Exception as error:

        print(
            "\nError loading PDF:"
        )

        print(error)

        exit()


    if not text.strip():

        print(
            "\nNo readable text was found "
            "inside the PDF."
        )

        print(
            "The PDF may be scanned or "
            "image-based."
        )

        exit()


    print(
        "PDF loaded successfully!"
    )

    print(
        "Total characters:",
        len(text)
    )

    # CHUNK DOCUMENT

    print(
        "\n[2/4] Splitting document "
        "into chunks..."
    )

    chunks = split_text(
        text
    )

    print(
        "Chunking completed!"
    )

    print(
        "Total chunks:",
        len(chunks)
    )


    if not chunks:

        print(
            "No chunks were created."
        )

        exit()


    # CREATE EMBEDDINGS

    print(
        "\n[3/4] Creating embeddings..."
    )

    try:

        embeddings = create_embeddings(
            chunks
        )

    except Exception as error:

        print(
            "\nError creating embeddings:"
        )

        print(error)

        exit()


    print(
        "Embeddings created successfully!"
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    # CREATE VECTOR DATABASE

    print(
        "\n[4/4] Creating FAISS "
        "vector database..."
    )

    index = create_vector_store(
        embeddings
    )

    print(
        "FAISS vector database created!"
    )

    print(
        "Vectors stored:",
        index.ntotal
    )

    # READY


    print(
        "           RAG SYSTEM READY"
    )

    print(
        "\nYou can now ask questions "
        "about your document."
    )

    print(
        "Type 'exit' to stop."
    )

    # QUESTION ANSWERING LOOP

    while True:

        question = input(
            "Ask a question: "
        ).strip()

        # EMPTY QUESTION

        if not question:

            print(
                "Please enter a question."
            )

            continue

        # EXIT

        if question.lower() in [
            "exit",
            "quit"
        ]:

            print(
                "\nExiting RAG system..."
            )

            print(
                "Goodbye!"
            )

            break

        # RETRIEVAL

        print(
            "\nSearching document..."
        )

        try:

            relevant_chunks = retrieve_chunks(
                question,
                index,
                chunks
            )

        except Exception as error:

            print(
                "\nError retrieving information:"
            )

            print(error)

            continue


        if not relevant_chunks:

            print(
                "\nNo relevant information found."
            )

            continue


        print(
            f"Retrieved "
            f"{len(relevant_chunks)} "
            f"relevant chunks."
        )

        # GENERATION

        print(
            "\nGenerating answer using Gemini..."
        )

        try:

            answer = generate_answer(
                question,
                relevant_chunks
            )

        except Exception as error:
            print(
                "ERROR GENERATING ANSWER"
            )


            print(error)

            print(
                "\nPossible causes:"
            )

            print(
                "1. Invalid Gemini API key"
            )

            print(
                "2. Gemini API quota exceeded"
            )

            print(
                "3. Model unavailable for your account"
            )

            print(
                "4. Internet connection problem"
            )

            continue


        # DISPLAY ANSWER

        print(
            "ANSWER"
        )

        print(
            answer
        )

        # DISPLAY SOURCES

        print(
            "RETRIEVED SOURCE CHUNKS"
        )

        for number, chunk in enumerate(
            relevant_chunks,
            start=1
        ):

            print(
                f"\n--- Source {number} ---"
            )

            print(
                chunk
            )