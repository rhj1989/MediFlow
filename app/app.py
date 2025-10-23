import reflex as rx
from app.states.auth_state import AuthState
from app.states.medicine_state import MedicineState
from app.states.auth_state import AuthState
from app.states.medicine_state import MedicineState
from app.states.supplier_state import SupplierState
from app.components.sidebar import sidebar
from app.components.dashboard import dashboard_component
from app.components.medicine import medicines_page
from app.components.supplier import suppliers_page
from app.states.db_state import create_tables

create_tables()


def protected_page(content: rx.Component) -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        rx.el.div(
            sidebar(),
            rx.el.main(content, class_name="flex-1 overflow-y-auto"),
            class_name="flex h-screen bg-gray-100 font-['Inter']",
        ),
        rx.el.div(),
    )


def index() -> rx.Component:
    return protected_page(dashboard_component())


def login_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.form(
                rx.el.div(
                    rx.el.h2(
                        "Login to MediFlow",
                        class_name="text-2xl font-bold text-center text-gray-800",
                    ),
                    rx.el.p(
                        "Default credentials: admin / admin",
                        class_name="text-sm text-center text-gray-500 mb-6",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Username", class_name="text-sm font-medium text-gray-700"
                        ),
                        rx.el.input(
                            placeholder="Enter your username",
                            name="username",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Password", class_name="text-sm font-medium text-gray-700"
                        ),
                        rx.el.input(
                            placeholder="Enter your password",
                            name="password",
                            type="password",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.p(
                            AuthState.error_message,
                            class_name="text-sm text-red-500 mb-4 text-center",
                        ),
                    ),
                    rx.el.button(
                        "Login",
                        type="submit",
                        class_name="w-full bg-orange-500 text-white p-2 rounded-md hover:bg-orange-600 transition-colors",
                    ),
                    class_name="flex flex-col",
                ),
                on_submit=AuthState.login,
            ),
            class_name="w-full max-w-sm p-8 bg-white rounded-xl shadow-lg border",
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-100 font-['Inter']",
    )


def placeholder_page(title: str) -> rx.Component:
    def page() -> rx.Component:
        return protected_page(
            rx.el.div(
                rx.el.h1(title, class_name="text-3xl font-bold text-gray-800"),
                class_name="p-6",
            )
        )

    return page


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=AuthState.on_load)
app.add_page(login_page, route="/login")
app.add_page(
    protected_page(medicines_page()),
    route="/medicines",
    on_load=[AuthState.on_load, MedicineState.load_medicines],
)
app.add_page(
    protected_page(suppliers_page()),
    route="/suppliers",
    on_load=[AuthState.on_load, SupplierState.load_suppliers],
)
from app.states.billing_state import BillingState
from app.states.purchase_state import PurchaseState
from app.components.billing import billing_page
from app.components.purchases import purchases_page

app.add_page(
    protected_page(billing_page()),
    route="/billing",
    on_load=[AuthState.on_load, BillingState.on_load],
)
app.add_page(
    protected_page(purchases_page()),
    route="/purchases",
    on_load=[AuthState.on_load, PurchaseState.load_dependencies],
)
from app.states.reports_state import ReportsState
from app.components.reports import reports_page

app.add_page(
    protected_page(reports_page()),
    route="/reports",
    on_load=[AuthState.on_load, ReportsState.fetch_report_data],
)
from app.states.settings_state import SettingsState
from app.components.settings import settings_page

app.add_page(
    protected_page(settings_page()), route="/settings", on_load=AuthState.on_load
)
from app.states.customer_state import CustomerState
from app.components.customer import customers_page
from app.states.prescription_state import PrescriptionState
from app.components.prescriptions import prescriptions_page

app.add_page(
    protected_page(customers_page()),
    route="/customers",
    on_load=[AuthState.on_load, CustomerState.load_customers],
)
app.add_page(
    protected_page(prescriptions_page()),
    route="/prescriptions",
    on_load=[AuthState.on_load, PrescriptionState.load_prescriptions],
)