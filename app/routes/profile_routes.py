from flask import (
    Blueprint,
    render_template
)

from app.services.auth_helpers import (
    login_required
)


profile_bp = Blueprint(
    "profile",
    __name__
)


@profile_bp.route(
    "/profile"
)
@login_required
def profile():
    """
    Display the authenticated user's shared profile page.

    Both admin and client accounts use this route.
    Role-specific profile features can be added later.
    """

    return render_template(
        "profile.html"
    )
