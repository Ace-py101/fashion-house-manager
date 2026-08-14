from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from app.services.auth_helpers import (
    current_user_id,
    login_required,
)

from app.services.message_service import (
    get_user_conversations,
    get_conversation,
    get_conversation_messages,
    send_message,
)


message_bp = Blueprint(
    "message",
    __name__,
)


# ============================================================
# MESSAGES INBOX
# ============================================================

@message_bp.route("/messages")
@login_required
def messages():
    """
    Display the authenticated user's messaging inbox.

    Both clients and business accounts use the same
    communication portal.
    """

    user_id = current_user_id()

    conversations = get_user_conversations(
        user_id
    )

    return render_template(
        "messages.html",
        conversations=conversations,
    )


# ============================================================
# NEW CONVERSATION
# ============================================================

@message_bp.route("/messages/new")
@login_required
def new_message():
    """
    Placeholder entry point for starting a new conversation.

    Vendor/client discovery and Marketplace integration will
    be connected in a later implementation stage.
    """

    return render_template(
        "message_new.html"
    )


# ============================================================
# CONVERSATION
# ============================================================

@message_bp.route(
    "/messages/<int:conversation_id>"
)
@login_required
def conversation(conversation_id):
    """
    Display one authorized conversation.
    """

    user_id = current_user_id()

    conversation = get_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        flash(
            "Conversation not found or access denied.",
            "error",
        )

        return redirect(
            url_for("message.messages")
        )

    conversation_messages = (
        get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
        )
    )

    return render_template(
        "message_conversation.html",
        conversation=conversation,
        messages=conversation_messages,
    )


# ============================================================
# SEND MESSAGE
# ============================================================

@message_bp.route(
    "/messages/<int:conversation_id>/send",
    methods=["POST"],
)
@login_required
def send_conversation_message(
    conversation_id
):
    """
    Send a message to an authorized conversation.
    """

    user_id = current_user_id()

    body = request.form.get(
        "body",
        "",
    )

    try:
        send_message(
            conversation_id=conversation_id,
            sender_id=user_id,
            body=body,
        )

        flash(
            "Message sent successfully.",
            "success",
        )

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

    except Exception:

        flash(
            "Unable to send message. Please try again.",
            "error",
        )

    return redirect(
        url_for(
            "message.conversation",
            conversation_id=conversation_id,
        )
    )
