from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from app.models.user import User

from app.services.auth_helpers import (
    login_required,
    current_user_id
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

    user = (
        User.query
        .filter_by(
            id=current_user_id()
        )
        .first()
    )

    if not user:

        flash(
            "Unable to locate your account.",
            "error"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )

    return render_template(
        "profile.html",
        user=user
    )
