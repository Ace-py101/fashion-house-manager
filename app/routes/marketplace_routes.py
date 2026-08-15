from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from app.services.auth_helpers import (
    current_user_id,
    login_required,
)

from app.services.marketplace_service import (
    get_published_listings,
    get_listing_by_id,
    get_business_user,
    get_business_listings,
    get_business_listing,
    create_listing,
    update_listing,
    publish_listing,
    archive_listing,
    start_listing_conversation,
)

from app.services.style_service import (
    get_all_styles,
    get_style_by_id,
)


marketplace_bp = Blueprint(
    "marketplace",
    __name__,
    url_prefix="/marketplace",
)


# ============================================================
# PUBLIC MARKETPLACE
# ============================================================

@marketplace_bp.route("/")
def marketplace():
    """
    Display published marketplace listings.

    Available to visitors, clients and business accounts.
    """

    listings = get_published_listings()

    return render_template(
        "marketplace.html",
        listings=listings,
    )


@marketplace_bp.route("/listing/<int:listing_id>")
def listing(listing_id):
    """
    Display one published marketplace listing.
    """

    marketplace_listing = get_listing_by_id(
        listing_id
    )

    if not marketplace_listing:
        abort(404)

    return render_template(
        "marketplace_listing.html",
        listing=marketplace_listing,
    )


# ============================================================
# BUSINESS MARKETPLACE MANAGEMENT
# ============================================================

@marketplace_bp.route("/manage")
@login_required
def manage_listings():
    """
    Display marketplace listings belonging to the
    authenticated business account.
    """

    user_id = current_user_id()

    business = get_business_user(user_id)

    if not business:
        flash(
            "Marketplace management is available to business accounts.",
            "error",
        )

        return redirect(
            url_for("marketplace.marketplace")
        )

    listings = get_business_listings(
        business.id
    )

    return render_template(
        "marketplace_manage.html",
        listings=listings,
    )


# ============================================================
# CREATE LISTING
# ============================================================

@marketplace_bp.route(
    "/manage/new",
    methods=["GET", "POST"],
)
@login_required
def new_listing():
    """
    Create a marketplace listing from an existing Style Gallery
    record.

    Marketplace listings intentionally do not accept independent
    title, description or category input. Those values are derived
    from the selected Style.
    """

    user_id = current_user_id()

    business = get_business_user(user_id)

    if not business:
        flash(
            "Only business accounts can create marketplace listings.",
            "error",
        )

        return redirect(
            url_for("marketplace.marketplace")
        )

    styles = get_all_styles()

    selected_style_id = request.args.get(
        "style_id",
        "",
    ).strip()

    if selected_style_id:

        if not selected_style_id.isdigit():

            flash(
                "The selected Style Gallery item is invalid.",
                "error",
            )

            return redirect(
                url_for(
                    "style.view_styles"
                )
            )

        selected_style = get_style_by_id(
            int(selected_style_id)
        )

        if not selected_style:

            flash(
                "The selected style could not be found.",
                "error",
            )

            return redirect(
                url_for(
                    "style.view_styles"
                )
            )

        if selected_style.status.lower() != "active":

            flash(
                "Only active styles can be published to the Marketplace.",
                "error",
            )

            return redirect(
                url_for(
                    "style.view_styles"
                )
            )

    else:

        selected_style_id = None

    if request.method == "POST":

        try:

            style_id = request.form.get(
                "style_id",
                "",
            ).strip()

            if not style_id.isdigit():
                raise ValueError(
                    "Please select a style from the Style Gallery."
                )

            style = get_style_by_id(
                int(style_id)
            )

            if not style:
                raise ValueError(
                    "The selected style could not be found."
                )

            if style.status.lower() != "active":
                raise ValueError(
                    "Only active styles can be published to the Marketplace."
                )

            listing = create_listing(
                business_id=business.id,
                style_id=style.id,
                title=style.style_name,
                description=None,
                category=style.garment_name,
                price=request.form.get(
                    "price",
                    "",
                ),
                currency=request.form.get(
                    "currency",
                    "NGN",
                ),
                image_path=style.image_filename,
                status=request.form.get(
                    "status",
                    "draft",
                ),
            )

            flash(
                "Marketplace listing created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "marketplace.edit_listing",
                    listing_id=listing.id,
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "error",
            )

        except Exception:

            flash(
                "Unable to create marketplace listing.",
                "error",
            )

    return render_template(
        "marketplace_listing_form.html",
        listing=None,
        styles=styles,
        selected_style_id=selected_style_id,
        form_mode="create",
    )



# ============================================================
# EDIT LISTING
# ============================================================

@marketplace_bp.route(
    "/manage/<int:listing_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_listing(listing_id):

    user_id = current_user_id()

    business = get_business_user(user_id)

    if not business:
        flash(
            "Only business accounts can manage marketplace listings.",
            "error",
        )

        return redirect(
            url_for("marketplace.marketplace")
        )

    listing = get_business_listing(
        listing_id=listing_id,
        business_id=business.id,
    )

    if not listing:
        abort(404)

    styles = get_all_styles()

    if request.method == "POST":

        try:

            style_id = request.form.get(
                "style_id",
                "",
            ).strip()

            if not style_id.isdigit():
                raise ValueError(
                    "Please select a style from the Style Gallery."
                )

            style = get_style_by_id(
                int(style_id)
            )

            if not style:
                raise ValueError(
                    "The selected style could not be found."
                )

            if style.status.lower() != "active":
                raise ValueError(
                    "Only active styles can be used for Marketplace listings."
                )

            description = request.form.get(
                "description",
                "",
            ).strip()

            if len(description) > 5000:
                raise ValueError(
                    "Product description cannot exceed 5000 characters."
                )

            update_listing(
                listing=listing,
                title=style.style_name,
                description=description or None,
                category=style.garment_name,
                price=request.form.get(
                    "price",
                    "",
                ),
                currency=request.form.get(
                    "currency",
                    "NGN",
                ),
                style_id=style.id,
                image_path=style.image_filename,
                status=request.form.get(
                    "status",
                    "draft",
                ),
            )

            flash(
                "Marketplace listing updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "marketplace.manage_listings"
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "error",
            )

        except Exception:

            flash(
                "Unable to update marketplace listing.",
                "error",
            )

    return render_template(
        "marketplace_listing_form.html",
        listing=listing,
        styles=styles,
        form_mode="edit",
    )



# ============================================================
# PUBLISH
# ============================================================

@marketplace_bp.route(
    "/manage/<int:listing_id>/publish",
    methods=["POST"],
)
@login_required
def publish_listing_route(listing_id):

    business = get_business_user(
        current_user_id()
    )

    if not business:
        flash(
            "Only business accounts can publish listings.",
            "error",
        )

        return redirect(
            url_for("marketplace.marketplace")
        )

    listing = get_business_listing(
        listing_id=listing_id,
        business_id=business.id,
    )

    if not listing:
        abort(404)

    try:

        publish_listing(listing)

        flash(
            "Marketplace listing published successfully.",
            "success",
        )

    except Exception:

        flash(
            "Unable to publish marketplace listing.",
            "error",
        )

    return redirect(
        url_for(
            "marketplace.manage_listings"
        )
    )


# ============================================================
# ARCHIVE
# ============================================================

@marketplace_bp.route(
    "/manage/<int:listing_id>/archive",
    methods=["POST"],
)
@login_required
def archive_listing_route(listing_id):

    business = get_business_user(
        current_user_id()
    )

    if not business:
        flash(
            "Only business accounts can archive listings.",
            "error",
        )

        return redirect(
            url_for("marketplace.marketplace")
        )

    listing = get_business_listing(
        listing_id=listing_id,
        business_id=business.id,
    )

    if not listing:
        abort(404)

    try:

        archive_listing(listing)

        flash(
            "Marketplace listing archived successfully.",
            "success",
        )

    except Exception:

        flash(
            "Unable to archive marketplace listing.",
            "error",
        )

    return redirect(
        url_for(
            "marketplace.manage_listings"
        )
    )

# ============================================================
# CONTACT VENDOR
# ============================================================

@marketplace_bp.route(
    "/listing/<int:listing_id>/contact",
    methods=["POST"],
)
@login_required
def contact_vendor(listing_id):
    """
    Start or retrieve a client-to-business conversation
    for a published marketplace listing.
    """

    user_id = current_user_id()

    listing = get_listing_by_id(
        listing_id
    )

    if not listing:
        abort(404)

    try:

        conversation, created = start_listing_conversation(
            listing=listing,
            client_id=user_id,
        )

        if created:
            flash(
                "Conversation started with the business.",
                "success",
            )
        else:
            flash(
                "Opening your existing conversation with the business.",
                "success",
            )

        return redirect(
            url_for(
                "message.conversation",
                conversation_id=conversation.id,
            )
        )

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

        return redirect(
            url_for(
                "marketplace.listing",
                listing_id=listing_id,
            )
        )

    except Exception:

        flash(
            "Unable to start the conversation. Please try again.",
            "error",
        )

        return redirect(
            url_for(
                "marketplace.listing",
                listing_id=listing_id,
            )
        )
