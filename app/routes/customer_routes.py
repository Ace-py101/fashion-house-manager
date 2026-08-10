from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.customer_service import (
    create_customer,
    get_all_customers,
    get_inactive_customers,
    activate_customer,
    search_customers,
    get_customer_by_id,
    update_customer,
    get_customer_history,
    deactivate_customer
)

from app.models.order import Order


customer_bp = Blueprint(
    "customer",
    __name__
)


@customer_bp.route("/customers")
def customers():

    return render_template(
        "customers.html"
    )


@customer_bp.route(
    "/customers/new",
    methods=["GET", "POST"]
)
def new_customer():

    style_id = request.args.get(
        "style_id",
        type=int
    )
 
    if request.method == "POST":

        customer_data = {

            "full_name": request.form.get(
                "full_name",
                ""
            ),

            "phone": request.form.get(
                "phone",
                ""
            ),

            "email": request.form.get(
                "email",
                ""
            ),

            "address": request.form.get(
                "address",
                ""
            ),

            "gender": request.form.get(
                "gender",
                ""
            ),

            "notes": request.form.get(
                "notes",
                ""
            )

        }

        result = create_customer(
            customer_data
        )

        if result["success"]:

            flash(
                "Customer created successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "order.new_order",
                    customer_code=result["customer"].customer_code,
                    style_id=style_id
                )
            )

        for error in result["errors"]:

            category = (
                "error"
                if "already exists" in error
                else "warning"
            )

            flash(
                error,
                category
            )

    return render_template(
        "new_customer.html"
    )


@customer_bp.route("/customers/view")
def view_customers():

    customers = get_all_customers()

    customer_stats = {}

    for customer in customers:

        customer_stats[customer.id] = {

            "orders": Order.query.filter_by(
                customer_id=customer.id
            ).count()

        }

    return render_template(
        "view_customers.html",
        customers=customers,
        customer_stats=customer_stats
    )

  
@customer_bp.route(
    "/customers/search",
    methods=["GET", "POST"]
)
def search_customer():

    customers = []

    query = ""

    style_id = request.args.get(
        "style_id",
        type=int
    )

    if request.method == "POST":

        query = request.form.get(
            "query",
            ""
        ).strip()

        style_id = request.form.get(
            "style_id",
            type=int
        )

        customers = search_customers(
            query
        )

    customer_stats = {}

    for customer in customers:

        customer_stats[customer.id] = {

            "orders": Order.query.filter_by(
                customer_id=customer.id
            ).count()

        }

    return render_template(

        "search_customer.html",

        customers=customers,

        query=query,

        customer_stats=customer_stats,

        style_id=style_id

    )


@customer_bp.route(
    "/customers/<int:customer_id>"
)
def view_customer(customer_id):

    style_id = request.args.get(
        "style_id",
        type=int
    )

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        flash(
            "Customer not found.",
            "error"
        )

        return redirect(
            url_for(
                "customer.customers"
            )
        )
 
        return redirect(
            url_for(
                "customer.view_customers"
            )
        )

    return render_template(
        "view_customer.html",
        customer=customer,
        sty_id=style_id,
        
    )


@customer_bp.route(
    "/customers/<int:customer_id>/edit",
    methods=["GET", "POST"]
)
def edit_customer(customer_id):

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        flash(
            "Customer not found.",
            "error"
        )

        return redirect(
            url_for(
                "customer.view_customers"
            )
        )

    if request.method == "POST":

        customer_data = {

            "full_name": request.form.get(
                "full_name",
                ""
            ),

            "phone": request.form.get(
                "phone",
                ""
            ),

            "email": request.form.get(
                "email",
                ""
            ),

            "address": request.form.get(
                "address",
                ""
            ),

            "gender": request.form.get(
                "gender",
                ""
            ),

            "notes": request.form.get(
                "notes",
                ""
            )

        }

        result = update_customer(
            customer_id,
            customer_data
        )

        if result["success"]:

            flash(
                "Customer updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "customer.view_customer",
                    customer_id=customer_id
                )
            )

        for error in result["errors"]:

            category = (
                "error"
                if "already exists" in error
                else "warning"
            )

            flash(
                error,
                category
            )

    return render_template(
        "edit_customer.html",
        customer=customer
    )


@customer_bp.route(
    "/customers/<int:customer_id>/history"
)
def customer_history(customer_id):

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        flash(
            "Customer not found.",
            "error"
        )

        return redirect(
            url_for(
                "customer.view_customers"
            )
        )

    history = get_customer_history(
        customer_id
    )

    return render_template(
        "customer_history.html",
        customer=customer,
        history=history
    )


@customer_bp.route(
    "/customers/<int:customer_id>/activity"
)
def customer_activity(customer_id):

    customer = get_customer_by_id(
        customer_id
    )

    if not customer:

        flash(
            "Customer not found.",
            "error"
        )

        return redirect(
            url_for(
                "customer.view_customers"
            )
        )

    total_orders = Order.query.filter_by(
        customer_id=customer.id
    ).count()

    return render_template(
        "customer_activity.html",
        customer=customer,
        total_orders=total_orders,
        production_orders=0,
        delivered_orders=0,
        amendment_orders=0,
        replacement_orders=0,
        total_measurements=0,
        outstanding_balance=0,
        lifetime_spending=0
    )
    
@customer_bp.route(
    "/customers/<int:customer_id>/deactivate",
    methods=["POST"]
)
def deactivate_customer_route(customer_id):

    result = deactivate_customer(
        customer_id
    )

    if result["success"]:

        flash(
            "Customer deactivated successfully.",
            "success"
        )

    else:

        for error in result["errors"]:

            flash(
                error,
                "error"
            )

    return redirect(
        url_for(
            "customer.view_customers"
        )
    )


@customer_bp.route(
    "/customers/inactive"
)
def inactive_customers():

    customers = get_inactive_customers()

    customer_stats = {}

    for customer in customers:

        customer_stats[customer.id] = {

            "orders": Order.query.filter_by(
                customer_id=customer.id
            ).count()

        }

    return render_template(
        "inactive_customers.html",
        customers=customers,
        customer_stats=customer_stats
    )


@customer_bp.route(
    "/customers/<int:customer_id>/activate",
    methods=["POST"]
)
def activate_customer_route(customer_id):

    result = activate_customer(
        customer_id
    )

    if result["success"]:

        flash(
            "Customer activated successfully.",
            "success"
        )

    else:

        for error in result["errors"]:

            flash(
                error,
                "error"
            )

    return redirect(
        url_for(
            "customer.inactive_customers"
        )
    )
