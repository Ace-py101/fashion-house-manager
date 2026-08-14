from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from app.services.auth_helpers import (
    login_required,
    current_user_id
)

from app.models.user import User

from app.services.auth_service import (
    register_user,
    authenticate_user,
    verify_email_token,
    resend_verification_email,
    request_password_reset,
    reset_password,
    VALID_ACCOUNT_TYPES,
    verify_phone_code,
    send_phone_verification_code,
)


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        try:

            email = request.form.get(
                "email",
                ""
            )

            phone_number = request.form.get(
                "phone_number",
                ""
            )

            password = request.form.get(
                "password",
                ""
            )

            confirm_password = request.form.get(
                "confirm_password",
                ""
            )

            account_type = request.form.get(
                "account_type",
                ""
            )

            user, email_sent = register_user(
                email=email,
                password=password,
                confirm_password=confirm_password,
                account_type=account_type,
                phone_number=phone_number
            )

            if email_sent:

                flash(
                    "Account created successfully. "
                    "Please check your email to verify your account.",
                    "success"
                )

            else:

                flash(
                    "Account created, but the verification email "
                    "could not be sent. Please contact support or "
                    "configure email delivery.",
                    "warning"
                )

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "error"
            )

        except Exception:

            flash(
                "Unable to create account. Please try again.",
                "error"
            )

    return render_template(
        "register.html",
        account_types=VALID_ACCOUNT_TYPES
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        try:

            user = authenticate_user(
                email=email,
                password=password
            )

            session.clear()

            session["user_id"] = user.id
            session["email"] = user.email
            session["account_type"] = user.account_type
            session["authenticated"] = True

            flash(
                "Login successful.",
                "success"
            )

            if user.account_type == "admin":

                return redirect(
                    url_for(
                        "main.index"
                    )
                )

            return redirect(
                url_for(
                    "marketplace.marketplace"
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "error"
            )

        except Exception:

            flash(
                "Unable to log in. Please try again.",
                "error"
            )

    return render_template(
        "login.html"
    )


@auth_bp.route(
    "/verify-email/<token>"
)
def verify_email(token):

    success, message = (
        verify_email_token(
            token
        )
    )

    if success:

        flash(
            message,
            "success"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )

    flash(
        message,
        "error"
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )


@auth_bp.route(
    "/logout"
)
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )



@auth_bp.route(
    "/resend-verification",
    methods=["POST"]
)
def resend_verification():

    email = request.form.get(
        "email",
        ""
    )

    success, message = resend_verification_email(
        email
    )

    flash(
        message,
        "success" if success else "warning"
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        )

        success, message = (
            request_password_reset(
                email
            )
        )

        if success:

            flash(
                message,
                "success"
            )

        else:

            flash(
                message,
                "warning"
            )

        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

    return render_template(
        "forgot_password.html"
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password_route(token):

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        success, message = reset_password(
            token=token,
            password=password,
            confirm_password=confirm_password
        )

        if success:

            flash(
                message,
                "success"
            )

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        flash(
            message,
            "error"
        )

        return redirect(
            url_for(
                "auth.reset_password_route",
                token=token
            )
        )

    return render_template(
        "reset_password.html",
        token=token
    )


# ============================================================
# PHONE VERIFICATION
# ============================================================

@auth_bp.route(
    "/verify-phone",
    methods=["GET", "POST"]
)
@login_required
def verify_phone():
    """
    Display and process the phone verification form.
    """

    user_id = current_user_id()

    user = (
        User.query
        .filter_by(id=user_id)
        .first()
    )

    if not user:

        flash(
            "Unable to locate your account.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        code = request.form.get(
            "verification_code",
            ""
        )

        success, message = (
            verify_phone_code(
                user,
                code
            )
        )

        flash(
            message,
            "success" if success else "error"
        )

        if success:

            return redirect(
                url_for("settings.settings")
            )

    return render_template(
        "verify_phone.html",
        user=user
    )


@auth_bp.route(
    "/send-phone-verification",
    methods=["POST"]
)
@login_required
def send_phone_verification():
    """
    Generate and send a phone verification OTP.

    Authentication and OTP lifecycle remain inside the service
    layer. The route only coordinates the HTTP request.
    """

    user_id = current_user_id()

    user = (
        User.query
        .filter_by(id=user_id)
        .first()
    )

    if not user:
        session.clear()

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    success, message = (
        send_phone_verification_code(
            user
        )
    )

    flash(
        message,
        "success" if success else "warning"
    )

    if success:
        return redirect(
            url_for("auth.verify_phone")
        )

    return redirect(
        url_for("settings.settings")
    )


@auth_bp.route(
    "/resend-phone-verification",
    methods=["POST"]
)
@login_required
def resend_phone_verification():
    """
    Generate and send a fresh phone verification OTP.

    The raw OTP remains inside the service layer and is never
    returned to the HTTP route.
    """

    user_id = current_user_id()

    user = (
        User.query
        .filter_by(id=user_id)
        .first()
    )

    if not user:
        session.clear()

        flash(
            "Your account session is no longer valid. "
            "Please log in again.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    success, message = (
        send_phone_verification_code(
            user
        )
    )

    if success:
        flash(
            "A new verification code has been sent "
            "to your phone.",
            "success"
        )

        return redirect(
            url_for("auth.verify_phone")
        )

    flash(
        message,
        "warning"
    )

    return redirect(
        url_for("auth.verify_phone")
    )
