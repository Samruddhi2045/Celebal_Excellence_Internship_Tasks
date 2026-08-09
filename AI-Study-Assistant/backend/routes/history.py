from flask import Blueprint, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from extensions import db

from models.conversation import Conversation
from models.chat_message import ChatMessage


history_bp = Blueprint(
    "history",
    __name__,
    url_prefix="/api/history"
)


@history_bp.route("", methods=["GET"])
@jwt_required()
def get_history():

    user_id = int(
        get_jwt_identity()
    )

    conversations = (
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(
            Conversation.created_at.desc()
        )
        .all()
    )

    history = []

    for conversation in conversations:

        messages = (
            ChatMessage.query
            .filter_by(
                conversation_id=conversation.id
            )
            .order_by(
                ChatMessage.created_at.asc()
            )
            .all()
        )

        history.append({

            "conversation_id":
                conversation.id,

            "document_id":
                conversation.document_id,

            "messages": [

                {
                    "id":
                        message.id,

                    "role":
                        message.role,

                    "content":
                        message.content,

                    "created_at":
                        message.created_at.isoformat()
                        if message.created_at
                        else None
                }

                for message in messages

            ]

        })

    return jsonify({

        "history":
            history

    }), 200


@history_bp.route(
    "/stats",
    methods=["GET"]
)
@jwt_required()
def get_stats():

    user_id = int(
        get_jwt_identity()
    )

    conversation_count = (
        Conversation.query
        .filter_by(
            user_id=user_id
        )
        .count()
    )


    conversations = (
        Conversation.query
        .filter_by(
            user_id=user_id
        )
        .all()
    )

    conversation_ids = [
        conversation.id
        for conversation in conversations
    ]



    question_count = 0

    if conversation_ids:

        question_count = (
            ChatMessage.query
            .filter(
                ChatMessage.conversation_id.in_(
                    conversation_ids
                ),
                ChatMessage.role == "user"
            )
            .count()
        )


    return jsonify({

        "conversations":
            conversation_count,

        "questions":
            question_count

    }), 200