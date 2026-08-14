from datetime import datetime

from app.database import db
from app.models.conversation import Conversation
from app.models.message import Message


# ============================================================
# MESSAGING SERVICE
# ============================================================
#
# Central business-logic layer for client <-> business
# communication.
#
# Routes should coordinate HTTP requests only.
# Conversation and message rules belong here.
#
# ============================================================


def _get_user_conversation(conversation_id, user_id):
    """
    Return a conversation only when the authenticated user
    participates in it.
    """

    if not conversation_id or not user_id:
        return None

    return (
        Conversation.query
        .filter(
            Conversation.id == conversation_id,
            (
                (Conversation.client_id == user_id)
                | (Conversation.business_id == user_id)
            ),
        )
        .first()
    )


def get_user_conversations(user_id):
    """
    Return all conversations belonging to the authenticated user.
    """

    if not user_id:
        return []

    return (
        Conversation.query
        .filter(
            (
                (Conversation.client_id == user_id)
                | (Conversation.business_id == user_id)
            )
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )


def get_conversation(conversation_id, user_id):
    """
    Return one conversation when the authenticated user
    participates in it.
    """

    return _get_user_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )


def get_or_create_conversation(
    client_id,
    business_id,
    order_id=None,
    listing_id=None,
):
    """
    Find an existing client/business conversation or create one.

    Conversations are unique within a client/business/order
    context.
    """

    if not client_id:
        raise ValueError(
            "A client account is required."
        )

    if not business_id:
        raise ValueError(
            "A business account is required."
        )

    if client_id == business_id:
        raise ValueError(
            "A user cannot create a conversation with the same account."
        )

    query = Conversation.query.filter(
        Conversation.client_id == client_id,
        Conversation.business_id == business_id,
    )

    if order_id is None:
        query = query.filter(
            Conversation.order_id.is_(None)
        )
    else:
        query = query.filter(
            Conversation.order_id == order_id
        )

    if listing_id is None:
        query = query.filter(
            Conversation.listing_id.is_(None)
        )
    else:
        query = query.filter(
            Conversation.listing_id == listing_id
        )

    conversation = query.first()

    if conversation:
        return conversation, False

    conversation = Conversation(
        client_id=client_id,
        business_id=business_id,
        order_id=order_id,
        listing_id=listing_id,
    )

    db.session.add(conversation)
    db.session.commit()

    return conversation, True


def send_message(
    conversation_id,
    sender_id,
    body,
):
    """
    Send a message inside an authorized conversation.
    """

    conversation = _get_user_conversation(
        conversation_id=conversation_id,
        user_id=sender_id,
    )

    if not conversation:
        raise ValueError(
            "Conversation not found or access denied."
        )

    if body is None:
        raise ValueError(
            "Message cannot be empty."
        )

    body = body.strip()

    if not body:
        raise ValueError(
            "Message cannot be empty."
        )

    if len(body) > 5000:
        raise ValueError(
            "Message cannot exceed 5000 characters."
        )

    message = Message(
        conversation_id=conversation.id,
        sender_id=sender_id,
        body=body,
    )

    db.session.add(message)

    conversation.updated_at = datetime.utcnow()

    db.session.commit()

    return message


def get_conversation_messages(
    conversation_id,
    user_id,
):
    """
    Return messages belonging to an authorized conversation.
    """

    conversation = _get_user_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        return None

    return (
        Message.query
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )
