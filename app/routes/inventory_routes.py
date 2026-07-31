from flask import Blueprint, render_template


inventory_bp = Blueprint(
    "inventory",
    __name__
)



@inventory_bp.route("/inventory")
def inventory():

    return render_template(
        "module_placeholder.html",
        module_name="Inventory"
    )
