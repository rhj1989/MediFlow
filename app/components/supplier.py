import reflex as rx
from app.states.supplier_state import SupplierState, Supplier


def supplier_form_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SupplierState.show_form,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                SupplierState.is_editing,
                                "Edit Supplier",
                                "Add New Supplier",
                            ),
                            class_name="text-lg font-semibold text-gray-800",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=SupplierState.toggle_form,
                            class_name="text-gray-500 hover:text-gray-800",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label("Name", class_name="text-sm font-medium"),
                                rx.el.input(
                                    default_value=SupplierState.form_data.get(
                                        "name", ""
                                    ),
                                    name="name",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Contact No", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=SupplierState.form_data.get(
                                        "contact_no", ""
                                    ),
                                    name="contact_no",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Address", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=SupplierState.form_data.get(
                                        "address", ""
                                    ),
                                    name="address",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-2",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 py-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=SupplierState.toggle_form,
                                class_name="px-4 py-2 bg-gray-200 rounded-md text-gray-700 hover:bg-gray-300",
                            ),
                            rx.el.button(
                                "Save",
                                type="submit",
                                class_name="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                            ),
                            class_name="flex justify-end gap-3 pt-4 border-t",
                        ),
                        on_submit=SupplierState.save_supplier,
                    ),
                    class_name="bg-white rounded-xl shadow-lg w-full max-w-xl p-6",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50",
            ),
        )
    )


def supplier_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Name", class_name="p-3 text-left"),
                    rx.el.th("Contact No", class_name="p-3 text-left"),
                    rx.el.th("Address", class_name="p-3 text-left"),
                    rx.el.th("Actions", class_name="p-3 text-center"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    SupplierState.filtered_suppliers,
                    lambda sup: rx.el.tr(
                        rx.el.td(sup["name"], class_name="p-3"),
                        rx.el.td(sup["contact_no"], class_name="p-3"),
                        rx.el.td(sup["address"], class_name="p-3"),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-4 w-4"),
                                    on_click=lambda: SupplierState.open_edit_form(sup),
                                    class_name="text-blue-500 hover:text-blue-700",
                                ),
                                rx.el.button(
                                    rx.icon("trash-2", class_name="h-4 w-4"),
                                    on_click=lambda: SupplierState.delete_supplier(
                                        sup["id"]
                                    ),
                                    class_name="text-red-500 hover:text-red-700",
                                ),
                                class_name="flex justify-center gap-2",
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


def suppliers_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Manage Suppliers", class_name="text-3xl font-bold text-gray-800"),
            rx.el.div(
                rx.el.input(
                    placeholder="Search by name...",
                    on_change=SupplierState.set_search_query,
                    class_name="p-2 border rounded-md w-full md:w-1/3",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Supplier",
                    on_click=SupplierState.open_add_form,
                    class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
        ),
        supplier_table(),
        supplier_form_modal(),
        class_name="p-6",
    )