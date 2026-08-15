from flask import (
    render_template,
    Blueprint,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)

from app.services.notification_service import (
    create_notification,
    get_user_notifications,
    get_unread_notification_count,
    mark_notification_read,
    mark_all_notifications_read,
)


notification_bp = Blueprint(
    "notification",
    __name__,
    url_prefix="/notifications",
)


def _get_authenticated_user_id():
    """
    Return the authenticated user's ID from the session.
    """

    if not session.get("authenticated"):
        return None

    return session.get("user_id")


@notification_bp.route("/")
def notifications():
    """
    Notification center.
    """

    user_id = _get_authenticated_user_id()

    if not user_id:
        flash(
            "Please sign in to view notifications.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    notification_list = get_user_notifications(
        user_id=user_id
    )

    unread_count = get_unread_notification_count(
        user_id=user_id
    )

    return jsonify(
        {
            "notifications": [
                {
                    "id": notification.id,
                    "type": notification.notification_type,
                    "title": notification.title,
                    "message": notification.message,
                    "link": notification.link,
                    "is_read": notification.is_read,
                    "created_at": (
                        notification.created_at.isoformat()
                    ),
                }
                for notification in notification_list
            ],
            "unread_count": unread_count,
        }
    )


@notification_bp.route(
    "/<int:notification_id>/read",
    methods=["POST"],
)
def mark_read(notification_id):
    """
    Mark one notification as read.
    """

    user_id = _get_authenticated_user_id()

    if not user_id:
        return jsonify(
            {
                "success": False,
                "message": "Authentication required.",
            }
        ), 401

    notification = mark_notification_read(
        notification_id=notification_id,
        user_id=user_id,
    )

    if not notification:
        return jsonify(
            {
                "success": False,
                "message": "Notification not found.",
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "unread_count": get_unread_notification_count(
                user_id
            ),
        }
    )


@notification_bp.route(
    "/read-all",
    methods=["POST"],
)
def mark_all_read():
    """
    Mark all notifications as read.
    """

    user_id = _get_authenticated_user_id()

    if not user_id:
        return jsonify(
            {
                "success": False,
                "message": "Authentication required.",
            }
        ), 401

    marked_count = mark_all_notifications_read(
        user_id=user_id
    )

    return jsonify(
        {
            "success": True,
            "marked_count": marked_count,
            "unread_count": 0,
        }
    )

# ============================================================
# ATELIIER FHM NOTIFICATION DETAIL PAGE
# ============================================================
#
# This is the human-facing destination for an individual
# notification.
#
# The JSON /notifications/ endpoint remains exclusively owned
# by the global notification JavaScript shell.
# ============================================================

@notification_bp.route("/<int:notification_id>")
def notification_detail(notification_id):
    """
    Render a human-readable notification detail page.
    """

    user_id = _get_authenticated_user_id()

    if not user_id:

        flash(
            "Please sign in to view notifications.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    notification_list = get_user_notifications(
        user_id=user_id
    )

    notification = next(
        (
            item
            for item in notification_list
            if item.id == notification_id
        ),
        None
    )

    if not notification:

        flash(
            "Notification not found.",
            "warning"
        )

        return redirect(
            url_for("notification.notification_history")
        )

    return render_template(
        "notification_detail.html",
        notification=notification
    )



# ============================================================
# DEVELOPMENT NOTIFICATION TEST
# ============================================================


# ============================================================
# DEVELOPMENT NOTIFICATION TEST
#
# Temporary controlled producer used to verify the complete
# global notification chain before real application modules
# begin producing notifications.
#
# This route intentionally uses the existing service layer.
# It must be removed after shell verification is complete.
# ============================================================

@notification_bp.route(
    "/test/create",
    methods=["POST"]
)
def create_test_notification():

    if not session.get("authenticated"):

        return jsonify({
            "success": False,
            "message": "Authentication required."
        }), 401

    user_id = session.get("user_id")

    notification = create_notification(
        user_id=user_id,
        notification_type="system",
        title="Ateliier Notification Test",
        message=(
            "This is a controlled test of the global "
            "Ateliier notification system."
        ),
        link=url_for(
            "notification.notification_history"
        )
    )

    return jsonify({
        "success": True,
        "notification": {
            "id": notification.id,
            "notification_type": (
                notification.notification_type
            ),
            "title": notification.title,
            "message": notification.message,
            "link": notification.link,
            "is_read": notification.is_read
        }
    })
# ============================================================
# ATELIIER FHM NOTIFICATION HISTORY PAGE
# ============================================================

@notification_bp.route("/all")
def notification_history():
    """
    Render the human-facing notification history page.

    The root /notifications/ endpoint remains the JSON API
    consumed by the global notification shell.
    """

    user_id = _get_authenticated_user_id()

    if not user_id:
        flash(
            "Please sign in to view notifications.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "notifications.html"
    )
