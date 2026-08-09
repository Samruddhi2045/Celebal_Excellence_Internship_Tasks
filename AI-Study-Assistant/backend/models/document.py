from datetime import datetime

from extensions import db


class Document(db.Model):

    __tablename__ = "documents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_type = db.Column(
        db.String(20),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    extracted_text = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="uploaded",
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "documents",
            lazy=True
        )
    )

    def to_dict(self):

        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "status": self.status,
            "uploaded_at": (
                self.uploaded_at.isoformat()
                if self.uploaded_at
                else None
            )
        }