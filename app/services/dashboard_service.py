from datetime import datetime

from app.models.customer import Customer



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




def get_dashboard_metrics():

    return {

        "total_customers": Customer.query.count()

    }
