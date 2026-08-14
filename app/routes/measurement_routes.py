from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.models.order import Order

from app.constants.measurement_templates import (
    get_measurement_template,
    garment_has_measurements
)

from app.services.auth_helpers import (
    admin_required
)

from app.services.document_service import (
    DocumentType,
    build_document_context,
    build_measurement_document_url
)

from app.services.measurement_service import (
    create_measurement,
    update_measurement,
    get_customer_for_measurement,
    get_all_measurements,
    get_measurement_by_id,
    get_measurements_by_order,
    search_measurements,
    get_measurement_history,
    get_measurement_activity
)


measurement_bp = Blueprint(
    "measurement",
    __name__
)

def build_measurement_data(
    measurement_sections,
    form_data
):
    """
    Build measurement_data dictionary
    from submitted form values.
    """

    measurement_data = {}

    for section_title, fields in measurement_sections:

        section_data = {}

        for field in fields:

            section_data[field] = form_data.get(
                field.lower().replace(
                    " ",
                    "_"
                ),
                ""
            )

        measurement_data[
            section_title
        ] = section_data

    return measurement_data

@measurement_bp.route("/measurements")
@admin_required
def measurements():

    return render_template(
        "measurements.html"
    )


@measurement_bp.route(
    "/measurements/new",
    methods=["GET", "POST"]
)
@admin_required
def new_measurement():

    customer = None

    eligible_orders = []

    order = None

    measurement_sections = []

    show_order_selection = True

    #
    # --------------------------------------------------
    # Direct launch from View Orders
    # --------------------------------------------------
    #

    order_code = (
        request.args.get(
            "order_id",
            ""
        ).strip()
    )

    if order_code:

        order = (
            Order.query
            .filter_by(
                order_id=order_code
            )
            .first()
        )

        if not order:

            flash(
                "Order not found.",
                "error"
            )

        else:

            if not garment_has_measurements(
                order.garment_name
            ):

                flash(
                    "No measurement template exists for this garment.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "order.view_orders"
                    )
                )

            customer = order.customer

            measurement_sections = (
                get_measurement_template(
                    order.garment_name
                )
            )

            show_order_selection = False

    #
    # --------------------------------------------------
    # Launch from Customer Search
    # --------------------------------------------------
    #

    customer_code = (
        request.args.get(
            "customer_code",
            ""
        ).strip()
    )

    if customer_code and not order:

        customer, eligible_orders = (
            get_customer_for_measurement(
                customer_code
            )
        )

        if not customer:

            flash(
                "Customer not found.",
                "error"
            )

    #
    # --------------------------------------------------
    # POST Requests
    # --------------------------------------------------
    #

    if request.method == "POST":

        action = (
            request.form.get(
                "action",
                ""
            )
        )

        #
        # Search Customer
        #

        if action == "search_customer":

            customer_code = (
                request.form.get(
                    "customer_code",
                    ""
                ).strip()
            )

            customer, eligible_orders = (
                get_customer_for_measurement(
                    customer_code
                )
            )

            if not customer:

                flash(
                    "Customer not found.",
                    "error"
                )

        #
        # Create Measurement
        #

        elif action == "create_measurement":

            order_code = (
                request.form.get(
                    "order_id",
                    ""
                ).strip()
            )

            order = (
                Order.query
                .filter_by(
                    order_id=order_code
                )
                .first()
            )

            if not order:

                flash(
                    "Order not found.",
                    "error"
                )

            else:

                if not garment_has_measurements(
                    order.garment_name
                ):

                    flash(
                        "No measurement template exists for this garment.",
                        "warning"
                    )

                    return redirect(
                        url_for(
                            "order.view_orders"
                        )
                    )

                customer = order.customer

                customer, eligible_orders = (
                    get_customer_for_measurement(
                        customer.customer_code
                    )
                )

                measurement_sections = (
                    get_measurement_template(
                        order.garment_name
                    )
                )

                show_order_selection = False
 
        #
        # Save Measurement
        #

        elif action == "save":

            order_code = (
                request.form.get(
                    "order_id",
                    ""
                ).strip()
            )
 
            order = (
                Order.query
                .filter_by(
                    order_id=order_code
                )
                .first()
            )

            if not order:

                flash(
                    "Order not found.",
                    "error"
                )

                return redirect(
                    url_for(
                        "measurement.new_measurement"
                    )
                )

            if not garment_has_measurements(
                order.garment_name
            ):

                flash(
                    "No measurement template exists for this garment.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "order.view_orders"
                    )
                )

            measurement_sections = (
                get_measurement_template(
                    order.garment_name
                )
            )

            measurement_data = build_measurement_data(
                measurement_sections,
                request.form
            )

            create_measurement(
            
                order_id=order.id,
            
                customer_id=order.customer_id,
            
                measurement_unit=request.form.get(
                    "measurement_unit"
                ),
            
                measurement_type=request.form.get(
                    "measurement_type",
                    "Initial"
                ),
            
                measurement_data=measurement_data,
            
                notes=request.form.get(
                    "notes"
                )
            
            )

            flash(
                "Measurements saved successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "measurement.new_measurement"
                )
            )

    return render_template(
        "new_measurement.html",
        customer=customer,
        eligible_orders=eligible_orders,
        order=order,
        measurement_sections=measurement_sections,
        show_order_selection=show_order_selection
    )

@measurement_bp.route(
    "/measurements/order/<order_id>"
)
@admin_required
def view_order_measurements(
    order_id
):

    order = (

        Order.query

        .filter_by(
            order_id=order_id
        )

        .first()

    )

    if not order:

        flash(
            "Order not found.",
            "error"
        )

        return redirect(
            url_for(
                "order.view_orders"
            )
        )

    measurements = (

        get_measurements_by_order(
            order.id
        )

    )

    return render_template(

        "view_order_measurements.html",

        order=order,

        customer=order.customer,

        measurements=measurements

    )

@measurement_bp.route(
    "/measurements/<int:measurement_id>"
)
@admin_required
def view_measurement(
    measurement_id
):

    measurement = (
        get_measurement_by_id(
            measurement_id
        )
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.measurements"
            )
        )

    order = measurement.order

    customer = measurement.customer

    return render_template(

        "view_measurement.html",

        measurement=measurement,

        order=order,

        customer=customer

    )

@measurement_bp.route(
    "/measurements/<int:measurement_id>/history"
)
@admin_required
def measurement_history(
    measurement_id
):

    measurement = get_measurement_by_id(
        measurement_id
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.search_measurements"
            )
        )

    history = get_measurement_history(
        measurement.id
    )

    customer = measurement.customer

    order = measurement.order

    return render_template(
        "measurement_history.html",
        measurement=measurement,
        customer=customer,
        order=order,
        history=history
    )

@measurement_bp.route(
    "/measurements/<int:measurement_id>/activity"
)
@admin_required
def measurement_activity(
    measurement_id
):

    measurement = get_measurement_by_id(
        measurement_id
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.search_measurements_route"
            )
        )

    activity = get_measurement_activity(
        measurement.id
    )

    return render_template(
        "measurement_activity.html",
        measurement=measurement,
        activity=activity
    )


# ==========================================================
# VIEW MEASUREMENTS
# ==========================================================

@measurement_bp.route(
    "/measurements/view"
)
@admin_required
def view_measurements():

    measurements = (
        get_all_measurements()
    )

    return render_template(
        "view_measurements.html",
        measurements=measurements
    )

    

# ==========================================================
# SEARCH MEASUREMENTS
# ==========================================================

@measurement_bp.route(
    "/measurements/search",
    methods=["GET"]
)
@admin_required
def search_measurements_route():

    keyword = (
        request.args.get(
            "keyword",
            ""
        ).strip()
    )

    measurements = None

    if keyword:

        measurements = (
            search_measurements(
                keyword
            )
        )

    return render_template(

        "search_measurements.html",

        keyword=keyword,

        measurements=measurements

    )

# ==========================================================
# PRINT MEASUREMENT (A4)
# ==========================================================

@measurement_bp.route(
    "/measurements/<int:measurement_id>/print"
)
@admin_required
def print_measurement(
    measurement_id
):

    measurement = (
        get_measurement_by_id(
            measurement_id
        )
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.view_measurements"
            )
        )

    context = build_document_context(
    
        document_type=DocumentType.MEASUREMENT,
    
        document_number=measurement.measurement_id,
    
        title="Measurement Sheet",
    
        customer=measurement.customer,
    
        order=measurement.order,
    
        measurement=measurement
    
    )
    
    context["measurement"] = measurement

    return render_template(

        "documents/measurement/print_a4.html",

        **context

    )

# ==========================================================
# SEND MEASUREMENT
# ==========================================================

@measurement_bp.route(
    "/measurements/<int:measurement_id>/send"
)
@admin_required
def send_measurement(
    measurement_id
):

    measurement = get_measurement_by_id(
        measurement_id
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.view_measurements"
            )
        )

    document_url = (
    
        build_measurement_document_url(
    
            measurement
    
        )
    
    )
    
    return render_template(
    
        "send_measurement.html",
    
        measurement=measurement,
    
        customer=measurement.customer,
    
        order=measurement.order,
    
        document_url=document_url
    
    )

# ==========================================================
# DOWNLOAD PDF
# ==========================================================

@measurement_bp.route(
    "/measurements/<int:measurement_id>/download/pdf"
)
@admin_required
def download_measurement_pdf(
    measurement_id
):

    measurement = get_measurement_by_id(
        measurement_id
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.view_measurements"
            )
        )

    context = build_document_context(

        document_type=DocumentType.MEASUREMENT,

        document_number=measurement.measurement_id,

        title="Measurement Sheet",

        customer=measurement.customer,

        order=measurement.order,

        measurement=measurement

    )

    context["measurement"] = measurement

    context["download_mode"] = True

    return render_template(

        "documents/measurement/print_a4.html",

        **context

    )

# ==========================================================
# EDIT MEASUREMENT
# ==========================================================

@measurement_bp.route(
    "/measurements/<int:measurement_id>/edit",
    methods=["GET", "POST"]
)
@admin_required
def edit_measurement(
    measurement_id
):

    measurement = get_measurement_by_id(
        measurement_id
    )

    if not measurement:

        flash(
            "Measurement not found.",
            "error"
        )

        return redirect(
            url_for(
                "measurement.view_measurements"
            )
        )

    customer = measurement.customer

    order = measurement.order

    if request.method == "POST":

        measurement_sections = get_measurement_template(
            order.garment_name
        )
        
        measurement_data = build_measurement_data(
            measurement_sections,
            request.form
        )
        
        update_measurement(
            measurement,
            request.form.get(
                "measurement_unit"
            ),
            request.form.get(
                "measurement_type"
            ),
            measurement_data,
            request.form.get(
                "notes"
            )
        )
         
        flash(
            "Measurement updated successfully.",
            "success"
        )
        
        return redirect(
            url_for(
                "measurement.view_measurement",
                measurement_id=measurement.id
            )
        )

        return redirect(
            url_for(
                "measurement.view_measurement",
                measurement_id=measurement.id
            )
        )

    return render_template(

        "edit_measurement.html",

        measurement=measurement,

        customer=customer,

        order=order,

        measurement_sections=get_measurement_template(
            order.garment_name
        )

    )    
