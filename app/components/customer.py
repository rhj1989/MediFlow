import reflex as rx
from app.states.customer_state import CustomerState, Customer


def customer_form_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            CustomerState.show_form,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                CustomerState.is_editing,
                                "Edit Customer",
                                "Add New Customer",
                            ),
                            class_name="text-lg font-semibold text-gray-800",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=CustomerState.toggle_form,
                            class_name="text-gray-500 hover:text-gray-800",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label("Name", class_name="text-sm font-medium"),
                                rx.el.input(
                                    default_value=CustomerState.form_data.get(
                                        "name", ""
                                    ),
                                    name="name",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                    required=True,
                                ),
                                class_name="col-span-1 md:col-span-2",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Phone Number", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=CustomerState.form_data.get(
                                        "phone", ""
                                    ),
                                    name="phone",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label("Email", class_name="text-sm font-medium"),
                                rx.el.input(
                                    default_value=CustomerState.form_data.get(
                                        "email", ""
                                    ),
                                    type="email",
                                    name="email",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Address", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=CustomerState.form_data.get(
                                        "address", ""
                                    ),
                                    name="address",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1 md:col-span-2",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 py-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=CustomerState.toggle_form,
                                class_name="px-4 py-2 bg-gray-200 rounded-md text-gray-700 hover:bg-gray-300",
                            ),
                            rx.el.button(
                                "Save",
                                type="submit",
                                class_name="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                            ),
                            class_name="flex justify-end gap-3 pt-4 border-t",
                        ),
                        on_submit=CustomerState.save_customer,
                    ),
                    class_name="bg-white rounded-xl shadow-lg w-full max-w-2xl p-6",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50",
            ),
        )
    )


def customer_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Name", class_name="p-3 text-left"),
                    rx.el.th("Phone", class_name="p-3 text-left"),
                    rx.el.th("Email", class_name="p-3 text-left"),
                    rx.el.th("Address", class_name="p-3 text-left"),
                    rx.el.th("Actions", class_name="p-3 text-center"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    CustomerState.filtered_customers,
                    lambda customer: rx.el.tr(
                        rx.el.td(customer["name"], class_name="p-3"),
                        rx.el.td(customer["phone"], class_name="p-3"),
                        rx.el.td(customer["email"], class_name="p-3"),
                        rx.el.td(customer["address"], class_name="p-3"),
                        rx.el.td(
                            rx.el.div(
                                rx.el.a(
                                    rx.icon("file-text", class_name="h-4 w-4"),
                                    rx.el.span(
                                        customer["prescription_count"],
                                        class_name="absolute -top-1 -right-1.5 h-4 w-4 rounded-full bg-green-500 text-white text-xs flex items-center justify-center",
                                    ),
                                    href=f"/prescriptions?customer_id={customer['id'].to_string()}",
                                    class_name="text-green-500 hover:text-green-700 relative group",
                                    rx_id=f"view-prescriptions-{customer['id'].to_string()}",
                                ),
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-4 w-4"),
                                    on_click=lambda: CustomerState.open_edit_form(
                                        customer
                                    ),
                                    class_name="text-blue-500 hover:text-blue-700",
                                ),
                                rx.el.button(
                                    rx.icon("trash-2", class_name="h-4 w-4"),
                                    on_click=lambda: CustomerState.delete_customer(
                                        customer["id"]
                                    ),
                                    class_name="text-red-500 hover:text-red-700",
                                ),
                                class_name="flex justify-center gap-3 items-center",
                            ),
                            class_name="p-3",
                        ),
                        class_name="border-b hover:bg-gray-50",
                    ),
                )
            ),
            class_name="w-full text-sm text-gray-700",
        ),
        class_name="w-full bg-white border rounded-xl shadow-sm overflow-hidden",
    )


def customers_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Manage Customers", class_name="text-3xl font-bold text-gray-800"),
            rx.el.div(
                rx.el.input(
                    placeholder="Search by name or phone...",
                    on_change=CustomerState.set_search_query,
                    class_name="p-2 border rounded-md w-full md:w-1/3",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Customer",
                    on_click=CustomerState.open_add_form,
                    class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
        ),
        customer_table(),
        customer_form_modal(),
        class_name="p-6",
    )