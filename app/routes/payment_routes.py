from flask import Blueprint, render_template


payment_bp = Blueprint(
    "payment",
    __name__
)



@payment_bp.route("/payments")
def payments():

    return render_template(
        "module_placeholder.html",
        module_name="Payments"
    )
