from functools import wraps

from flask import (
    flash,
    redirect,
    session,
    url_for
)


# ============================================================
# AUTHENTICATION STATE
#
# These helpers provide the common authentication state used
# throughout the application.
#
# Authentication and authorization remain separate:
#
#   Authentication = "Who is logged in?"
#   Authorization  = "What may that account access?"
# ============================================================


def is_authenticated():
    """
    Return True when the current session belongs
    to an authenticated user.
    """

    return bool(
        session.get("authenticated")
        and session.get("user_id")
    )


def current_user_id():
    """
    Return the authenticated user's ID.

    Returns None when no authenticated user exists.
    """

    if not is_authenticated():
        return None

    return session.get("user_id")


def current_account_type():
    """
    Return the authenticated user's account type.

    Returns None when no authenticated user exists.
    """

    if not is_authenticated():
        return None

    return session.get("account_type")


# ============================================================
# LOGIN REQUIRED
#
# Any route using this decorator requires an authenticated
# session, regardless of account type.
# ============================================================


def login_required(view):
    """
    Require an authenticated user before
    allowing access to a route.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if not is_authenticated():

            flash(
                "Please log in to continue.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        return view(
            *args,
            **kwargs
        )

    return wrapped_view


# ============================================================
# ACCOUNT TYPE REQUIRED
#
# Restrict a route to one or more specific account types.
#
# Examples:
#
#     @account_type_required("admin")
#
#     @account_type_required("admin", "client")
#
# IMPORTANT:
#
# An unauthorized client must NOT be redirected to main.index
# because main.index is the admin dashboard.
#
# Clients are redirected to their own dashboard:
#
#     marketplace.marketplace
#
# This prevents an authorization redirect loop.
# ============================================================


def account_type_required(*allowed_types):
    """
    Restrict a route to specific account types.
    """

    def decorator(view):

        @wraps(view)
        def wrapped_view(*args, **kwargs):

            # ------------------------------------------------
            # No authenticated session.
            # ------------------------------------------------

            if not is_authenticated():

                flash(
                    "Please log in to continue.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "auth.login"
                    )
                )

            account_type = current_account_type()

            # ------------------------------------------------
            # Account is authenticated but does not have the
            # required account type.
            # ------------------------------------------------

            if account_type not in allowed_types:

                flash(
                    "You are not authorized to access that page.",
                    "error"
                )

                # --------------------------------------------
                # Client accounts belong in the client
                # dashboard, not the admin dashboard.
                # --------------------------------------------

                if account_type == "client":

                    return redirect(
                        url_for(
                            "marketplace.marketplace"
                        )
                    )

                # --------------------------------------------
                # Unknown or unsupported account type.
                #
                # Return to login rather than redirecting to
                # another protected route.
                # --------------------------------------------

                return redirect(
                    url_for(
                        "auth.login"
                    )
                )

            return view(
                *args,
                **kwargs
            )

        return wrapped_view

    return decorator


# ============================================================
# ADMIN REQUIRED
#
# Only admin accounts may access routes protected by this
# decorator.
# ============================================================


def admin_required(view):
    """
    Require an authenticated admin account.
    """

    return account_type_required(
        "admin"
    )(view)


# ============================================================
# CLIENT REQUIRED
#
# Only client accounts may access routes protected by this
# decorator.
# ============================================================


def client_required(view):
    """
    Require an authenticated client account.
    """

    return account_type_required(
        "client"
    )(view)
