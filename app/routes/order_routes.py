from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.models.customer import Customer

from app.models.style import Style

from app.constants.garments import VALID_GARMENT_NAMES

from app.models.measurement import Measurement

from app.services.auth_helpers import (
    admin_required
)

from app.services.order_service import (
    create_order,
    generate_order_id,
    get_all_orders,
    get_order_by_id,
    search_orders,
    get_order_history,
    get_order_activity, 
    update_order,
    update_order_status,
    VALID_ORDER_TYPES,
    VALID_FULFILLMENT_TYPES,
    VALID_ORDER_STATUSES,
)

order_bp = Blueprint(
    "order",
    __name__
)


@order_bp.route("/orders")
@admin_required
def orders():
    return render_template(
        "orders.html"
    )


@order_bp.route("/orders/new", methods=["GET", "POST"])
@admin_required
def new_order():

    customer = None
    order_id = None

    prefilled_customer_code = request.args.get(
        "customer_code",
        ""
    )
    
    prefilled_style_id = request.args.get(
        "style_id",
        type=int
    )

    selected_style = None

    if prefilled_style_id:
        selected_style = Style.query.get(
            prefilled_style_id
        )

    if prefilled_customer_code:
        
            customer = (
                Customer.query
                .filter_by(
                    customer_code=prefilled_customer_code
                )
                .first()
            )
        
            if customer:
                order_id = generate_order_id()    
      
    if request.method == "POST":

        action = request.form.get(
            "action"
        )

        if action == "search_customer":

            customer_code = request.form.get(
                "customer_code",
                ""
            ).strip()

            customer = (
                Customer.query
                .filter_by(
                    customer_code=customer_code
                )
                .first()
            )

            if customer:

                order_id = generate_order_id()

            else:

                flash(
                    "Customer not found.",
                    "error"
                )

        elif action == "save_order":

            customer_id = None

            try:

                customer_id = int(
                    request.form.get(
                        "customer_id"
                    )
                )

                order_type = request.form.get(
                    "order_type",
                    "new"
                )

                if order_type not in VALID_ORDER_TYPES:
                    raise ValueError(
                        "Invalid order type."
                    )

                fulfillment_type = request.form.get(
                    "fulfillment_type",
                    "custom"
                )

                size = request.form.get(
                    "size"
                )
                
                if (
                    fulfillment_type
                    not in VALID_FULFILLMENT_TYPES
                ):
                    raise ValueError(
                        "Invalid fulfillment type."
                    )

                garment_name = request.form.get(
                    "garment_name"
                )

                fabric_name = request.form.get(
                    "fabric_name"
                )

                delivery_date = datetime.strptime(
                    request.form.get(
                        "delivery_date"
                    ),
                    "%Y-%m-%d"
                ).date()

                price = float(
                    request.form.get(
                        "price"
                    )
                )

                deposit = float(
                    request.form.get(
                        "deposit"
                    )
                )

                status = request.form.get(
                    "status",
                    "new"
                )

                if status not in VALID_ORDER_STATUSES:
                
                    raise ValueError(
                        "Invalid order status."
                    ) 

                notes = request.form.get(
                    "notes"
                )

                style_id = request.form.get(
                    "style_id",
                    type=int
                )
                
                selected_style = None
                
                if style_id:
                    selected_style = Style.query.get(
                        style_id
                    )
                
                    if not selected_style:
                        raise ValueError(
                            "Selected style not found."
                        )

                create_order(
                    customer_id=customer_id,
                    order_type=order_type,
                    fulfillment_type=fulfillment_type,
                    size=size,
                    garment_name=garment_name,
                    fabric_name=fabric_name,
                    delivery_date=delivery_date,
                    price=price,
                    deposit=deposit,
                    style_id=style_id,
                    status=status,
                    notes=notes
                )
 
                flash(
                    "Order created successfully.",
                    "success"
                )

                return redirect(
                    url_for(
                        "order.new_order"
                    )
                )

            except Exception as error:

                flash(
                    str(error),
                    "error"
                )

                if customer_id:

                    customer = Customer.query.get(
                        customer_id
                    )

                order_id = generate_order_id()
        
    return render_template(
        "new_order.html",
        customer=customer,
        order_id=order_id,
        prefilled_customer_code=prefilled_customer_code,
        style_id=prefilled_style_id,
        selected_style=selected_style,
        order_types=VALID_ORDER_TYPES,
        fulfillment_types=VALID_FULFILLMENT_TYPES,
        order_statuses=VALID_ORDER_STATUSES,
        garment_names=VALID_GARMENT_NAMES
    )
 

@order_bp.route("/orders/view")
@admin_required
def view_orders():

    orders = get_all_orders()

    measurement_counts = {}
    
    for order in orders:
    
        measurement_counts[
            order.id
        ] = (
    
            Measurement.query
    
            .filter_by(
                order_id=order.id
            )
    
            .count()
    
        )

    return render_template(
    
        "view_orders.html",
    
        orders=orders,
    
        measurement_counts=measurement_counts
    
    )


@order_bp.route(
    "/orders/search",
    methods=["GET", "POST"]
)


@order_bp.route(
    "/orders/search",
    methods=["GET", "POST"]
)
@admin_required
def search_order():

    order = None

    if request.method == "POST":

        order_id = request.form.get(
            "order_id",
            ""
        ).strip()

        prefilled_style_id = request.form.get(
            "style_id",
            type=int
        )

        if order_id:

            order = get_order_by_id(
                order_id
            )

            if order is None:

                flash(
                    "Order not found.",
                    "warning"
                )

    return render_template(
        "search_order.html",
        order=order
    )


@order_bp.route("/orders/view/<order_id>")
@admin_required
def view_order(order_id):

    order = get_order_by_id(
        order_id
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

    return render_template(
        "view_order.html",
        order=order
    )


@order_bp.route(
    "/orders/edit/<order_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_order(order_id):

    order = get_order_by_id(
        order_id
    )

    selected_style_id = request.args.get(
        "style_id",
        type=int
    )
    
    selected_style = None
    
    if selected_style_id:
        selected_style = Style.query.get(
            selected_style_id
        )
    
        if not selected_style:
            flash(
                "Selected style not found.",
                "warning"
            )
    
            selected_style = None

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

    if request.method == "POST":

        try:

            order_type = request.form.get(
                "order_type",
                "new"
            )

            if order_type not in VALID_ORDER_TYPES:
                raise ValueError(
                    "Invalid order type."
                )

            fulfillment_type = request.form.get(
                "fulfillment_type",
                getattr(
                    order,
                    "fulfillment_type",
                    "custom"
                )
            )

            if (
                fulfillment_type
                not in VALID_FULFILLMENT_TYPES
            ):
                raise ValueError(
                    "Invalid fulfillment type."
                )

            size = request.form.get(
                "size"
            )

            style_id = request.form.get(
                "style_id",
                type=int
            )
            
            if style_id:
                selected_style = Style.query.get(
                    style_id
                )
            
                if not selected_style:
                    raise ValueError(
                        "Selected style not found."
                    )
        
            garment_name = request.form.get(
                "garment_name"
            )

            fabric_name = request.form.get(
                "fabric_name"
            )

            delivery_date = datetime.strptime(
                request.form.get(
                    "delivery_date"
                ),
                "%Y-%m-%d"
            ).date()

            price = float(
                request.form.get(
                    "price"
                )
            )

            deposit = float(
                request.form.get(
                    "deposit"
                )
            )

            status = request.form.get(
                "status",
                "new"
            )

            if status not in VALID_ORDER_STATUSES:
                raise ValueError(
                    "Invalid order status."
                )

            notes = request.form.get(
                "notes"
            )

            style_image = request.files.get(
                "style_image"
            )

            style_image_name = None

            if (
                style_image
                and style_image.filename
            ):

                style_image_name = (
                    style_image.filename
                )

            order.fulfillment_type = (
                fulfillment_type
            )

            update_order(
                order=order,
                fulfillment_type=fulfillment_type,
                size=size,
                garment_name=garment_name,
                fabric_name=fabric_name,
                delivery_date=delivery_date,
                price=price,
                deposit=deposit,
                style_id=style_id,
                style_image=style_image_name,
                status=status,
                notes=notes
            )

            flash(
                "Order updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "order.view_order",
                    order_id=order.order_id
                )
            )

        except Exception as error:

            flash(
                str(error),
                "error"
            )

    return render_template(
        "edit_order.html",
        order=order,
        styles=Style.query.all(),
        selected_style=selected_style,
        order_types=VALID_ORDER_TYPES,
        fulfillment_types=VALID_FULFILLMENT_TYPES,
        order_statuses=VALID_ORDER_STATUSES,
        garment_names=VALID_GARMENT_NAMES
    )


@order_bp.route(
    "/orders/status/<order_id>",
    methods=["GET", "POST"]
)
@admin_required
def change_order_status(order_id):

    order = get_order_by_id(
        order_id
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

    if request.method == "POST":

        status = request.form.get(
            "status"
        )

        if not status:

            flash(
                "Please select an order status.",
                "warning"
            )

            return redirect(
                url_for(
                    "order.change_order_status",
                    order_id=order.order_id
                )
            )

        update_order_status(
            order,
            status
        )

        flash(
            "Order status updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "order.view_order",
                order_id=order.order_id
            )
        )

    return render_template(
        "change_order_status.html",
        order=order,
        order_statuses=VALID_ORDER_STATUSES
    )


@order_bp.route("/orders/history/<order_id>")
@admin_required
def order_history(order_id):

    order = get_order_by_id(
        order_id
    )

    if not order:

        flash(
            "Order not found.",
            "error"
        )

        return redirect(
            url_for(
                "order.search_order"
            )
        )

    history = get_order_history(
        order.id
    )

    return render_template(
        "order_history.html",
        order=order,
       history=history
    )

@order_bp.route("/orders/activity/<order_id>")
@admin_required
def order_activity(order_id):

    order = get_order_by_id(
        order_id
    )

    if not order:

        flash(
            "Order not found.",
            "error"
        )

        return redirect(
            url_for(
                "order.search_order"
            )
        )

    activity = get_order_activity(
        order
    )

    return render_template(
        "order_activity.html",
        order=order,
        activity=activity
    )
