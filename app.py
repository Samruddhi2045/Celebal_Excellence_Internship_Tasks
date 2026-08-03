import streamlit as st
import tempfile
import os

from rag import (
    load_pdf,
    split_text,
    create_embeddings,
    create_vector_store,
    retrieve_chunks,
    generate_answer
)

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Document RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# CUSTOM CSS

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #888888;
        margin-bottom: 30px;
    }

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(0, 200, 100, 0.1);
        border: 1px solid rgba(0, 200, 100, 0.3);
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# HEADER

st.markdown(
    '<div class="main-title"> Document RAG Assistant</div>',
    unsafe_allow_html=True
)

# INITIALIZE SESSION STATE

if "index" not in st.session_state:
    st.session_state.index = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_name" not in st.session_state:
    st.session_state.document_name = None

# SIDEBAR

with st.sidebar:

    st.header(" Document")

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )

    if st.button(
        " Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

# PROCESS UPLOADED PDF

if uploaded_file is not None:

    # Process only if a different document was uploaded
    if (
        st.session_state.document_name
        != uploaded_file.name
    ):

        with st.spinner(
            "Processing document..."
        ):

            try:

                # SAVE TEMPORARY PDF

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getvalue()
                    )

                    temp_path = temp_file.name

                # LOAD PDF

                text = load_pdf(
                    temp_path
                )


                # Delete temporary file
                os.remove(
                    temp_path
                )


                if not text.strip():

                    st.error(
                        "No readable text was found "
                        "inside this PDF."
                    )

                    st.stop()

                # CHUNK TEXT
                chunks = split_text(
                    text
                )

                # CREATE EMBEDDINGS

                embeddings = create_embeddings(
                    chunks
                )

                # CREATE FAISS INDEX

                index = create_vector_store(
                    embeddings
                )

                # STORE IN SESSION

                st.session_state.chunks = chunks

                st.session_state.index = index

                st.session_state.document_name = (
                    uploaded_file.name
                )

                # Clear previous document chat
                st.session_state.messages = []


            except Exception as error:

                st.error(
                    f"Error processing PDF: {error}"
                )

                st.stop()


        st.success(
            "Document processed successfully!"
        )

# DOCUMENT INFORMATION

if st.session_state.index is not None:

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Document",
            st.session_state.document_name
        )

    with col2:

        st.metric(
            "Text Chunks",
            len(st.session_state.chunks)
        )

    with col3:

        st.metric(
            "Vectors",
            st.session_state.index.ntotal
        )

    st.divider()

# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        # Display sources for assistant responses
        if (
            message["role"] == "assistant"
            and "sources" in message
        ):

            with st.expander(
                "📚 View Retrieved Sources"
            ):

                for number, source in enumerate(
                    message["sources"],
                    start=1
                ):

                    st.markdown(
                        f"### Source {number}"
                    )

                    st.write(
                        source
                    )

                    st.divider()

# CHAT INPUT

if st.session_state.index is not None:

    question = st.chat_input(
        "Ask a question about your document..."
    )


    if question:

        # SAVE USER MESSAGE

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # DISPLAY USER MESSAGE

        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )

        # GENERATE ANSWER

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Searching document and generating answer..."
            ):

                try:

                    relevant_chunks = retrieve_chunks(
                        question,
                        st.session_state.index,
                        st.session_state.chunks
                    )

                    answer = generate_answer(
                        question,
                        relevant_chunks
                    )


                except Exception as error:

                    st.error(
                        f"Error generating answer: {error}"
                    )

                    st.stop()

            # DISPLAY ANSWER

            st.markdown(
                answer
            )

            # DISPLAY SOURCES

            with st.expander(
                " View Retrieved Sources"
            ):

                for number, source in enumerate(
                    relevant_chunks,
                    start=1
                ):

                    st.markdown(
                        f"### Source {number}"
                    )

                    st.write(
                        source
                    )

                    st.divider()

        # SAVE ASSISTANT MESSAGE

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": relevant_chunks
            }
        )

# NO DOCUMENT

else:

    st.info(
        " Upload a PDF from the sidebar to start asking questions."
    )

    st.markdown(
        """
        ### Try documents such as:

        - Resume
        - College notes
        - Research paper
        - Study material
        - Reports
        - Articles
        - Books
        """
    )