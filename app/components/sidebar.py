import reflex as rx
from app.states.auth_state import AuthState

NAV_ITEMS = [
    {"label": "Dashboard", "icon": "layout-dashboard", "href": "/"},
    {"label": "Medicines", "icon": "pill", "href": "/medicines"},
    {"label": "Customers", "icon": "users", "href": "/customers"},
    {"label": "Prescriptions", "icon": "file-text", "href": "/prescriptions"},
    {"label": "Suppliers", "icon": "truck", "href": "/suppliers"},
    {"label": "Billing", "icon": "file-scan", "href": "/billing"},
    {"label": "Purchases", "icon": "shopping-cart", "href": "/purchases"},
    {"label": "Reports", "icon": "bar-chart-2", "href": "/reports"},
    {"label": "Settings", "icon": "settings", "href": "/settings"},
]


def nav_item(item: dict) -> rx.Component:
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5 mr-3"),
        rx.el.span(item["label"]),
        href=item["href"],
        class_name="flex items-center p-2 rounded-md text-gray-700 hover:bg-orange-100 hover:text-orange-600 transition-colors",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("syringe", class_name="h-8 w-8 text-orange-500"),
                rx.el.span("MediFlow", class_name="text-xl font-bold text-gray-800"),
                class_name="flex h-16 items-center gap-2 border-b px-4",
            ),
            rx.el.nav(
                rx.foreach(NAV_ITEMS, nav_item), class_name="flex flex-col gap-1 p-4"
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.image(
                            src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.username}",
                            class_name="size-10 rounded-full",
                        ),
                        rx.el.div(
                            rx.el.p(
                                AuthState.username, class_name="font-semibold text-sm"
                            ),
                            rx.el.p("Admin", class_name="text-xs text-gray-500"),
                        ),
                    ),
                    rx.el.button(
                        rx.icon("log-out", class_name="h-5 w-5"),
                        on_click=AuthState.logout,
                        class_name="text-gray-500 hover:text-orange-600",
                    ),
                    class_name="flex items-center justify-between",
                ),
                class_name="mt-auto border-t p-4",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="hidden md:flex flex-col w-64 border-r bg-gray-50 h-screen",
    )