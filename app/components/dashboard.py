import reflex as rx
from app.states.db_state import DBState


def stat_card(icon: str, title: str, value: rx.Var, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6"),
            class_name=f"p-3 rounded-full bg-{color}-100 text-{color}-600",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value.to_string(), class_name="text-3xl font-bold text-gray-900"),
            class_name="flex flex-col",
        ),
        class_name="flex items-center gap-4 p-6 bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def dashboard_component() -> rx.Component:
    return rx.el.div(
        rx.el.h1("Dashboard", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            stat_card("users", "Total Customers", DBState.total_customers, "purple"),
            stat_card("pill", "Total Medicines", DBState.total_medicines, "blue"),
            stat_card(
                "package-minus", "Low Stock Items", DBState.low_stock_items, "yellow"
            ),
            stat_card(
                "indian-rupee",
                "Today's Sales",
                DBState.todays_sales.to_string(),
                "green",
            ),
            stat_card("calendar-clock", "Expiry Alerts", DBState.expiry_alerts, "red"),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6",
        ),
        class_name="p-6",
    )