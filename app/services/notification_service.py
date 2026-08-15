"""
Global notification service.

All application modules should use this service to create,
retrieve and update in-app notifications.

The notification shell is intentionally kept separate from
module-specific business logic.
"""

from app.database import db
from app.models.notification import Notification
from app.models.user_notification_preference import (
    UserNotificationPreference
)


VALID_NOTIFICATION_TYPES = {
    "order",
    "delivery",
    "message",
    "payment",
    "security",
    "marketplace",
    "firm_activity",
    "system",
    "marketing",
}


def _normalize_text(value, field_name, max_length):
    """
    Normalize and validate notification text.
    """

    value = (value or "").strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed "
            f"{max_length} characters."
        )

    return value


def _notification_enabled(user_id, notification_type):
    """
    Determine whether in-app notifications are enabled for the user.

    If a preference record does not yet exist, in-app notifications
    remain enabled by default.
    """

    preferences = (
        UserNotificationPreference.query
        .filter(
            UserNotificationPreference.user_id == user_id
        )
        .first()
    )

    if not preferences:
        return True

    if not preferences.in_app_enabled:
        return False

    if notification_type == "order":
        return preferences.order_notifications

    if notification_type == "delivery":
        return preferences.delivery_notifications

    if notification_type == "security":
        return preferences.security_notifications

    if notification_type == "marketing":
        return preferences.marketing_notifications

    return True


def create_notification(
    user_id,
    notification_type,
    title,
    message,
    link=None,
):
    """
    Create an in-app notification for a user.

    Returns:
        Notification instance when created.
        None when the user's in-app notification preference
        disables the notification.
    """

    if not user_id:
        raise ValueError(
            "A notification recipient is required."
        )

    if notification_type not in VALID_NOTIFICATION_TYPES:
        raise ValueError(
            "Invalid notification type."
        )

    title = _normalize_text(
        title,
        "Notification title",
        200
    )

    message = _normalize_text(
        message,
        "Notification message",
        1000
    )

    if link is not None:
        link = link.strip()

        if len(link) > 500:
            raise ValueError(
                "Notification link cannot exceed 500 characters."
            )

    if not _notification_enabled(
        user_id,
        notification_type
    ):
        return None

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )

    db.session.add(notification)
    db.session.commit()

    return notification


def get_user_notifications(
    user_id,
    limit=50,
):
    """
    Return the latest notifications belonging to a user.
    """

    if not user_id:
        return []

    if not isinstance(limit, int):
        limit = 50

    limit = max(1, min(limit, 100))

    return (
        Notification.query
        .filter(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(limit)
        .all()
    )


def get_unread_notification_count(user_id):
    """
    Return the number of unread notifications belonging
    to the authenticated user.
    """

    if not user_id:
        return 0

    return (
        Notification.query
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )


def mark_notification_read(
    notification_id,
    user_id,
):
    """
    Mark one notification as read only when it belongs
    to the authenticated user.
    """

    notification = (
        Notification.query
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if not notification:
        return None

    notification.is_read = True

    db.session.commit()

    return notification


def mark_all_notifications_read(user_id):
    """
    Mark all unread notifications for the authenticated user
    as read.
    """

    if not user_id:
        return 0

    count = (
        Notification.query
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .update(
            {
                Notification.is_read: True
            },
            synchronize_session=False,
        )
    )

    db.session.commit()

    return count
