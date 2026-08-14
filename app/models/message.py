from datetime import datetime

from app.database import db


class Message(db.Model):
    """
    Represents an individual message inside a conversation.

    Delivery, notification, attachment and read-receipt
    behavior will be implemented later.
    """

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    body = db.Column(
        db.Text,
        nullable=False
    )

    read_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    conversation = db.relationship(
        "Conversation",
        back_populates="messages"
    )

    sender = db.relationship(
        "User",
        backref="messages"
    )

    def __repr__(self):
        return (
            f"<Message "
            f"id={self.id} "
            f"conversation_id={self.conversation_id} "
            f"sender_id={self.sender_id}>"
        )
