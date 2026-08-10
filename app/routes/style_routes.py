from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.style_service import (
    create_style,
    get_all_styles,
    get_style_by_id,
    search_styles,
    VALID_STYLE_TYPES,
    VALID_OCCASION_FITS,
    VALID_GARMENT_NAMES,
    VALID_GENDERS,
    VALID_STATUSES
)

from app.models.customer import Customer


style_bp = Blueprint(
    "style",
    __name__
)


@style_bp.route(
    "/styles"
)
def styles():

    return render_template(
        "styles.html"
    )


@style_bp.route(
    "/styles/new",
    methods=["GET", "POST"]
)
def new_style():

    order_id = request.args.get(
        "order_id"
    )

    if request.method == "POST":

        image = request.files.get(
            "style_image"
        )

        if not image:
            flash(
                "Please choose an image.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        style_name = request.form.get(
            "style_name",
            ""
        ).strip()

        style_type = request.form.get(
            "style_type",
            ""
        ).strip()

        occasion_fit = request.form.get(
            "occasion_fit",
            ""
        ).strip()

        garment_name = request.form.get(
            "garment_name",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        fabric_requirement = request.form.get(
            "fabric_requirement",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        ).strip()

        if not style_name:
            flash(
                "Please enter a style name.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if style_type not in VALID_STYLE_TYPES:
            flash(
                "Please select a valid style type.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if occasion_fit not in VALID_OCCASION_FITS:
            flash(
                "Please select a valid occasion fit.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if garment_name not in VALID_GARMENT_NAMES:
            flash(
                "Please select a valid garment name.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if gender not in VALID_GENDERS:
            flash(
                "Please select a valid gender.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if not fabric_requirement:
            flash(
                "Please enter the fabric requirement.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        if status not in VALID_STATUSES:
            flash(
                "Please select a valid status.",
                "warning"
            )

            return redirect(
                url_for(
                    "style.new_style",
                    order_id=order_id
                )
            )

        create_style(
            image_file=image,
            style_name=style_name,
            style_type=style_type,
            occasion_fit=occasion_fit,
            garment_name=garment_name,
            gender=gender,
            fabric_requirement=fabric_requirement,
            status=status
        )

        flash(
            "Style uploaded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "style.new_style",
                order_id=order_id
            )
        )

    return render_template(
        "new_style.html",
        styles=get_all_styles(),
        order_id=order_id,
        style_types=VALID_STYLE_TYPES,
        occasion_fits=VALID_OCCASION_FITS,
        garment_names=VALID_GARMENT_NAMES,
        genders=VALID_GENDERS,
        statuses=VALID_STATUSES
    )

@style_bp.route(
    "/styles/view"
)
def view_styles():

    styles = get_all_styles()

    return render_template(
        "view_styles.html",
        styles=styles
    )

@style_bp.route(
    "/styles/search",
    methods=["GET"]
)
def search_styles_route():

    keyword = request.args.get(
        "keyword",
        ""
    )

    styles = []

    if keyword.strip():

        styles = search_styles(
            keyword
        )

    return render_template(

        "search_styles.html",

        keyword=keyword,

        styles=styles
    )


@style_bp.route(
    "/styles/<int:style_id>/make-order",
    methods=["GET", "POST"]
)
def make_order(style_id):

    style = get_style_by_id(
        style_id
    )

    if not style:

        flash(
            "Style not found.",
            "error"
        )

        return redirect(
            url_for(
                "style.new_style"
            )
        )


    if request.method == "POST":

        customer_code = request.form.get(
            "customer_code",
            ""
        ).strip()


        if not customer_code:

            flash(
                "Please enter a customer code.",
                "warning"
            )

            return render_template(
                "style_order_choice.html",
                style=style
            )


        customer = (
            Customer.query
            .filter_by(
                customer_code=customer_code
            )
            .first()
        )


        if not customer:

            flash(
                "Customer not found.",
                "error"
            )

            return render_template(
                "style_order_choice.html",
                style=style
            )


        return redirect(
            url_for(
                "order.new_order",
                customer_code=customer.customer_code,
                style_id=style.id
            )
        )


    return render_template(
        "style_order_choice.html",
        style=style
    )


@style_bp.route(
    "/styles/<int:style_id>"
)
def view_style(style_id):

    style = get_style_by_id(
        style_id
    )

    if not style:

        flash(
            "Style not found.",
            "error"
        )

        return redirect(
            url_for(
                "style.view_styles"
            )
        )

    return render_template(

        "view_style.html",

        style=style
    )
