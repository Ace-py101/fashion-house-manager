from flask import Blueprint, render_template


order_bp = Blueprint(
    "order",
    __name__
)



@order_bp.route("/orders")
def orders():

    return render_template(
        "module_placeholder.html",
        module_name="Orders"
    )
