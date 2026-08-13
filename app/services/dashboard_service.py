from datetime import datetime, date, timedelta

from app.models.customer import Customer
from app.models.order import Order
from app.models.measurement import Measurement


def get_greeting():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good Morning"

    elif 12 <= hour < 17:
        return "Good Afternoon"

    elif 17 <= hour < 22:
        return "Good Evening"

    else:
        return "Good Night"


def format_delivery_date(delivery_date):

    today = date.today()
    tomorrow = today + timedelta(days=1)

    if delivery_date == today:
        return "Today"

    if delivery_date == tomorrow:
        return "Tomorrow"

    return delivery_date.strftime(
        "%d %b %Y"
    )


def get_dashboard_metrics():

    active_orders = (
        Order.query
        .filter(
            Order.status.in_(
                [
                    "new",
                    "cutting",
                    "sewing"
                ]
            )
        )
        .count()
    )

    recent_orders = (
        Order.query
        .order_by(
            Order.created_at.desc()
        )
        .limit(5)
        .all()
    )

    upcoming_deliveries = (
        Order.query
        .filter(
            Order.delivery_date >= date.today()
        )
        .order_by(
            Order.delivery_date.asc()
        )
        .limit(5)
        .all()
    )

    # ============================================================
    # MEASUREMENT METRICS
    # ============================================================

    total_measurements = (
        Measurement.query.count()
    )

    male_measurements = (
        Measurement.query
        .join(Customer)
        .filter(
            Customer.gender.ilike("male")
        )
        .count()
    )

    female_measurements = (
        Measurement.query
        .join(Customer)
        .filter(
            Customer.gender.ilike("female")
        )
        .count()
    )

    # Children measurement classification will be implemented
    # later when the customer demographic architecture supports
    # an explicit child category.
    children_measurements = 0

    return {

        # ========================================================
        # CUSTOMER METRICS
        # ========================================================

        "total_customers":
            Customer.query.count(),

        "active_customers":
            Customer.query.filter_by(
                status="Active"
            ).count(),

        "inactive_customers":
            Customer.query.filter_by(
                status="Inactive"
            ).count(),

        # ========================================================
        # ORDER METRICS
        # ========================================================

        "total_orders":
            Order.query.count(),

        "active_orders":
            active_orders,

        "new_orders":
            Order.query.filter_by(
                status="new"
            ).count(),

        "cutting_orders":
            Order.query.filter_by(
                status="cutting"
            ).count(),

        "sewing_orders":
            Order.query.filter_by(
                status="sewing"
            ).count(),

        "fitting_orders":
            Order.query.filter_by(
                status="fitting"
            ).count(),

        "alteration_orders":
            Order.query.filter_by(
                status="alteration"
            ).count(),

        "ready_orders":
            Order.query.filter_by(
                status="ready"
            ).count(),

        "delivered_orders":
            Order.query.filter_by(
                status="delivered"
            ).count(),

        "cancelled_orders":
            Order.query.filter_by(
                status="cancelled"
            ).count(),

        # ========================================================
        # MEASUREMENT METRICS
        # ========================================================

        "total_measurements":
            total_measurements,

        "male_measurements":
            male_measurements,

        "female_measurements":
            female_measurements,

        "children_measurements":
            children_measurements,

        # ========================================================
        # DASHBOARD LISTS
        # ========================================================

        "recent_orders":
            recent_orders,

        "upcoming_deliveries":
            upcoming_deliveries,

        "format_delivery_date":
            format_delivery_date
    }
