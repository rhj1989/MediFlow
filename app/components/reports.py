import reflex as rx
from app.states.reports_state import ReportsState

REPORT_TABS = {
    "sales": {"label": "Sales Report", "icon": "indian-rupee"},
    "stock": {"label": "Stock Report", "icon": "boxes"},
    "expiry": {"label": "Expiry Report", "icon": "calendar-clock"},
    "low_stock": {"label": "Low Stock Report", "icon": "package-minus"},
    "supplier_purchases": {"label": "Supplier Purchases", "icon": "truck"},
    "customer_purchases": {"label": "Customer Purchases", "icon": "user-check"},
}


def report_tabs() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            list(REPORT_TABS.items()),
            lambda item: rx.el.button(
                rx.icon(item[1]["icon"], class_name="h-4 w-4 mr-2"),
                item[1]["label"],
                on_click=lambda: ReportsState.set_active_report(item[0]),
                class_name=rx.cond(
                    ReportsState.active_report == item[0],
                    "flex items-center px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg",
                    "flex items-center px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg",
                ),
            ),
        ),
        class_name="flex flex-wrap gap-2 mb-6",
    )


def report_filters() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.label("Start Date", class_name="text-sm font-medium"),
            rx.el.input(
                type="date",
                default_value=ReportsState.start_date,
                on_change=ReportsState.set_start_date,
                class_name="mt-1 p-2 border rounded-md w-full",
            ),
            class_name="w-full md:w-auto",
        ),
        rx.el.div(
            rx.el.label("End Date", class_name="text-sm font-medium"),
            rx.el.input(
                type="date",
                default_value=ReportsState.end_date,
                on_change=ReportsState.set_end_date,
                class_name="mt-1 p-2 border rounded-md w-full",
            ),
            class_name="w-full md:w-auto",
        ),
        rx.el.button(
            rx.icon("search", class_name="h-4 w-4 mr-2"),
            "Apply Filter",
            on_click=ReportsState.fetch_report_data,
            class_name="flex items-center h-10 px-4 mt-6 bg-orange-500 text-white rounded-md hover:bg-orange-600",
        ),
        class_name="flex flex-wrap gap-4 items-start mb-6",
    )


def report_table() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ReportsState.loading,
            rx.el.div(
                rx.spinner(class_name="text-orange-500 h-8 w-8"),
                class_name="flex justify-center items-center p-8",
            ),
            rx.cond(
                ReportsState.report_data.length() > 0,
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.foreach(
                                ReportsState.report_data[0].keys(),
                                lambda key: rx.el.th(
                                    key.to_string().replace("_", " ").capitalize(),
                                    class_name="p-3 text-left font-semibold",
                                ),
                            )
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            ReportsState.report_data,
                            lambda row: rx.el.tr(
                                rx.foreach(
                                    row.values(),
                                    lambda value: rx.el.td(
                                        value.to_string(), class_name="p-3"
                                    ),
                                ),
                                class_name="border-b hover:bg-gray-50",
                            ),
                        )
                    ),
                    class_name="w-full text-sm text-gray-700",
                ),
                rx.el.div(
                    "No data available for the selected criteria.",
                    class_name="p-8 text-center text-gray-500",
                ),
            ),
        ),
        class_name="w-full bg-white border rounded-xl shadow-sm overflow-x-auto",
    )


def reports_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Reports", class_name="text-3xl font-bold text-gray-800"),
            rx.el.button(
                rx.icon("cloud_download", class_name="h-4 w-4 mr-2"),
                "Download CSV",
                on_click=ReportsState.download_csv,
                class_name="flex items-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        report_tabs(),
        rx.cond(
            ReportsState.active_report.contains("date")
            | (ReportsState.active_report == "customer_purchases"),
            report_filters(),
        ),
        report_table(),
        class_name="p-6",
    )