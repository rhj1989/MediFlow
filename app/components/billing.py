import reflex as rx
from app.states.billing_state import BillingState, CartItem, MedicineSearchResult


def medicine_search_results() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            BillingState.search_results,
            lambda med: rx.el.div(
                rx.el.p(
                    f"{med['name']} ({med['batch_no']}) - Stock: {med['quantity']} {med['unit'] | ''}"
                ),
                on_click=lambda: BillingState.add_to_cart(med),
                class_name="p-2 hover:bg-gray-100 cursor-pointer rounded-md",
            ),
        ),
        class_name="absolute top-full left-0 right-0 bg-white border rounded-b-md shadow-lg z-10 max-h-60 overflow-y-auto",
    )


def cart_item_row(item: CartItem) -> rx.Component:
    return rx.el.tr(
        rx.el.td(f"{item['name']} ({item['batch_no']})", class_name="p-3"),
        rx.el.td(f"{item['sale_price']:.2f}", class_name="p-3"),
        rx.el.td(
            rx.el.div(
                rx.el.input(
                    type="number",
                    on_change=lambda val: BillingState.update_cart_quantity(
                        item["id"], val
                    ),
                    class_name="w-20 p-1 border rounded-md text-center",
                    default_value=item["quantity"].to_string(),
                ),
                rx.el.span(item["unit"], class_name="ml-2 text-sm text-gray-500"),
                class_name="flex items-center",
            ),
            class_name="p-3",
        ),
        rx.el.td(f"{item['subtotal']:.2f}", class_name="p-3 text-right font-medium"),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: BillingState.remove_from_cart(item["id"]),
                class_name="text-red-500 hover:text-red-700",
            ),
            class_name="p-3 text-center",
        ),
        class_name="border-b",
    )


def customer_selection() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Select Customer (Optional)",
            class_name="text-sm font-medium text-gray-700 mb-1",
        ),
        rx.el.select(
            rx.el.option("Walk-in Customer", value=""),
            rx.foreach(
                BillingState.customers,
                lambda c: rx.el.option(c["name"], value=c["id"].to_string()),
            ),
            on_change=BillingState.set_selected_customer_id,
            default_value=BillingState.selected_customer_id,
            class_name="w-full p-3 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500",
        ),
        rx.cond(
            BillingState.customer_prescriptions.length() > 0,
            rx.el.div(
                rx.el.label(
                    "Load from Prescription",
                    class_name="text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.select(
                    rx.el.option("Select a prescription to load...", value=""),
                    rx.foreach(
                        BillingState.customer_prescriptions,
                        lambda p: rx.el.option(
                            p["display_text"], value=p["id"].to_string()
                        ),
                    ),
                    on_change=BillingState.load_prescription_into_cart,
                    default_value=BillingState.selected_prescription_id,
                    class_name="w-full p-3 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500",
                ),
                class_name="w-full",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Doctor's Name (Optional)",
                class_name="text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.input(
                placeholder="Enter doctor's name",
                on_change=BillingState.set_doctor_name,
                default_value=BillingState.doctor_name,
                class_name="w-full p-3 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500",
            ),
            class_name="w-full",
        ),
        class_name="w-full mb-6 space-y-4",
    )


def billing_cart() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Current Bill", class_name="text-xl font-semibold text-gray-800 mb-4"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Medicine", class_name="p-3 text-left"),
                        rx.el.th("Price", class_name="p-3 text-left"),
                        rx.el.th("Qty", class_name="p-3 text-left"),
                        rx.el.th("Subtotal", class_name="p-3 text-right"),
                        rx.el.th("", class_name="p-3"),
                    )
                ),
                rx.el.tbody(rx.foreach(BillingState.cart_items, cart_item_row)),
                class_name="w-full text-sm text-gray-700",
            ),
            class_name="w-full bg-white border rounded-xl shadow-sm overflow-hidden mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Total Amount:", class_name="text-lg font-semibold"),
                rx.el.p(
                    f"\t{BillingState.total_amount:.2f}",
                    class_name="text-2xl font-bold text-orange-600",
                ),
                class_name="text-right",
            ),
            rx.el.div(
                rx.el.button(
                    "Clear Bill",
                    on_click=BillingState.clear_bill_event,
                    class_name="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300",
                ),
                rx.el.button(
                    rx.icon("file-scan", class_name="h-4 w-4 mr-2"),
                    "Generate Bill",
                    on_click=BillingState.generate_bill,
                    class_name="flex items-center px-6 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                class_name="flex justify-end items-center gap-4 mt-4",
            ),
            class_name="p-6 bg-white border rounded-xl shadow-sm",
        ),
        class_name="w-full lg:w-2/3",
    )


def billing_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Billing / Point of Sale",
            class_name="text-3xl font-bold text-gray-800 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("search", class_name="h-5 w-5 text-gray-400"),
                        class_name="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none",
                    ),
                    rx.el.input(
                        placeholder="Search for medicines by name or batch number...",
                        on_change=BillingState.search_medicines.debounce(300),
                        class_name="w-full p-3 pl-10 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500",
                    ),
                    rx.cond(BillingState.search_query != "", medicine_search_results()),
                    class_name="relative w-full mb-8",
                ),
                customer_selection(),
                billing_cart(),
                class_name="flex flex-col items-center",
            )
        ),
        class_name="p-6",
    )