from datetime import datetime

from extensions import db


class ChatMessage(db.Model):

    __tablename__ = "chat_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "conversations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):

        return {

            "id":
                self.id,

            "conversation_id":
                self.conversation_id,

            "role":
                self.role,

            "content":
                self.content,

            "created_at":
                self.created_at.isoformat()
                if self.created_at
                else None

        }