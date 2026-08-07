from datetime import datetime, date, timedelta

from app.models.customer import Customer
from app.models.order import Order


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


    return {


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



        "total_measurements":
            0,


        "male_measurements":
            0,


        "female_measurements":
            0,


        "children_measurements":
            0,



        "recent_orders":
            recent_orders,



        "upcoming_deliveries":
            upcoming_deliveries,



        "format_delivery_date":
            format_delivery_date

    }
