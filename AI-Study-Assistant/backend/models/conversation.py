from datetime import datetime

from extensions import db


class Conversation(db.Model):

    __tablename__ = "conversations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    document_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(255),
        nullable=False,
        default="New Conversation"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    messages = db.relationship(
        "ChatMessage",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    def to_dict(self):

        return {

            "id": self.id,

            "user_id":
                self.user_id,

            "document_id":
                self.document_id,

            "title":
                self.title,

            "created_at":
                self.created_at.isoformat()
                if self.created_at
                else None,

            "updated_at":
                self.updated_at.isoformat()
                if self.updated_at
                else None

        }