from flask import (
    Blueprint,
    request,
    jsonify
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from models.document import Document
from models.conversation import Conversation
from models.chat_message import ChatMessage

from rag.chat import search_document
from services.rag_service import index_document
from services.llm_service import generate_answer

from extensions import db

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)

@chat_bp.route(
    "/<int:document_id>",
    methods=["POST"]
)
@jwt_required()
def chat_with_document(document_id):

    print("CHAT REQUEST")

    user_id = int(
        get_jwt_identity()
    )

    print(
        "User ID:",
        user_id
    )

    print(
        "Document ID:",
        document_id
    )

    data = request.get_json(
        silent=True
    ) or {}


    question = (
        data.get("question")
        or ""
    ).strip()


    conversation_id = data.get(
        "conversation_id"
    )


    print(
        "Question:",
        question
    )

    print(
        "Conversation ID:",
        conversation_id
    )


    if not question:

        return jsonify({

            "detail":
            "Question is required."

        }), 400


    document = Document.query.filter_by(

        id=document_id,

        user_id=user_id

    ).first()


    if not document:

        return jsonify({

            "detail":
            "Document not found."

        }), 404


    print(
        "Document:",
        document.filename
    )

    print(
        "Status:",
        document.status
    )

    if not document.extracted_text:

        return jsonify({

            "detail":
            "This document does not contain extracted text."

        }), 400

    conversation = None


    if conversation_id:

        try:

            conversation_id = int(
                conversation_id
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "detail":
                "Invalid conversation ID."

            }), 400


        conversation = Conversation.query.filter_by(

            id=conversation_id,

            user_id=user_id,

            document_id=document_id

        ).first()


        if not conversation:

            return jsonify({

                "detail":
                "Conversation not found."

            }), 404


    else:

        conversation = Conversation(

            user_id=user_id,

            document_id=document_id,

            title=question[:255]

        )

        db.session.add(
            conversation
        )

        db.session.commit()


        print(
            "Created conversation:",
            conversation.id
        )

    user_message = ChatMessage(

        conversation_id=
            conversation.id,

        role="user",

        content=question

    )


    db.session.add(
        user_message
    )

    db.session.commit()


    print(
        "User message saved:",
        user_message.id
    )

    try:

        from rag.vector_store import (
            load_vector_store
        )


        index, metadata = load_vector_store(

            user_id,

            document_id

        )


        if index is None:

            print(
                "FAISS index not found."
            )

            print(
                "Creating index now..."
            )


            rag_result = index_document(

                user_id=user_id,

                document_id=document_id,

                text=document.extracted_text

            )


            document.status = "ready"


            db.session.commit()


            print(
                "FAISS index created."
            )

            print(
                "Chunks:",
                rag_result["chunks"]
            )


    except Exception as error:

        print(
            "INDEXING ERROR:",
            repr(error)
        )


        return jsonify({

            "detail":
            "Could not create the document search index.",

            "error":
            str(error)

        }), 500


    try:

        print(
            "Starting semantic search..."
        )


        results = search_document(

            user_id=user_id,

            document_id=document_id,

            question=question,

            top_k=5

        )


        print(
            "Search completed."
        )


        print(
            "Results:",
            len(results)
        )


    except Exception as error:

        print(
            "SEARCH ERROR:",
            repr(error)
        )


        return jsonify({

            "detail":
            "Could not search the document.",

            "error":
            str(error)

        }), 500


    if not results:

        answer = (
            "I couldn't find relevant information "
            "in this document."
        )


        # Save AI response

        ai_message = ChatMessage(

            conversation_id=
                conversation.id,

            role="assistant",

            content=answer

        )


        db.session.add(
            ai_message
        )

        db.session.commit()


        return jsonify({

            "conversation_id":
                conversation.id,

            "question":
                question,

            "answer":
                answer,

            "document": {

                "id":
                    document.id,

                "filename":
                    document.filename

            },

            "sources": []

        }), 200

    context_parts = []


    for result in results:

        context_parts.append(
            result["text"]
        )


    context = "\n\n".join(
        context_parts
    )


    print(
        "Context length:",
        len(context)
    )


    try:

        print(
            "Sending context to Groq..."
        )


        answer = generate_answer(

            question=question,

            context=context

        )


        print(
            "LLM answer generated."
        )


    except Exception as error:

        print(
            "LLM ERROR:",
            repr(error)
        )



        try:

            db.session.delete(
                user_message
            )

            db.session.commit()

        except Exception:

            db.session.rollback()


        return jsonify({

            "detail":
            "Could not generate AI answer.",

            "error":
            str(error)

        }), 500


    ai_message = ChatMessage(

        conversation_id=
            conversation.id,

        role="assistant",

        content=answer

    )


    db.session.add(
        ai_message
    )

    # Keep the first question as the title.

    if not conversation.title:

        conversation.title = (
            question[:255]
        )


    db.session.commit()


    print(
        "AI message saved:",
        ai_message.id
    )

    print(
        "CHAT SUCCESS"
    )

    print(
        "================================\n"
    )


    return jsonify({

        "conversation_id":
            conversation.id,

        "question":
            question,

        "answer":
            answer,

        "document": {

            "id":
                document.id,

            "filename":
                document.filename

        },

        "sources": [

            {

                "chunk_id":
                    result["chunk_id"],

                "score":
                    result["score"],

                "text":
                    result["text"]

            }

            for result in results

        ]

    }), 200