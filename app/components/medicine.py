import reflex as rx
from app.states.medicine_state import MedicineState, Medicine


def medicine_form_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            MedicineState.show_form,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                MedicineState.is_editing,
                                "Edit Medicine",
                                "Add New Medicine",
                            ),
                            class_name="text-lg font-semibold text-gray-800",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=MedicineState.toggle_form,
                            class_name="text-gray-500 hover:text-gray-800",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label("Name", class_name="text-sm font-medium"),
                                rx.el.input(
                                    default_value=MedicineState.form_data.get(
                                        "name", ""
                                    ),
                                    name="name",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Drug Type", class_name="text-sm font-medium"
                                ),
                                rx.el.select(
                                    rx.foreach(
                                        MedicineState.drug_types,
                                        lambda dt: rx.el.option(dt, value=dt),
                                    ),
                                    default_value=MedicineState.form_data.get(
                                        "drug_type", ""
                                    ),
                                    name="drug_type",
                                    placeholder="Select a drug type",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Batch No", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=MedicineState.form_data.get(
                                        "batch_no", ""
                                    ),
                                    name="batch_no",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Expiry Date", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    type="date",
                                    default_value=MedicineState.form_data.get(
                                        "expiry_date", ""
                                    ),
                                    name="expiry_date",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label("Unit", class_name="text-sm font-medium"),
                                rx.el.select(
                                    rx.foreach(
                                        MedicineState.medicine_units,
                                        lambda unit: rx.el.option(unit, value=unit),
                                    ),
                                    default_value=MedicineState.form_data.get(
                                        "unit", ""
                                    ),
                                    name="unit",
                                    placeholder="Select a unit",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Quantity", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value=MedicineState.form_data.get(
                                        "quantity", ""
                                    ).to_string(),
                                    name="quantity",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Purchase Price", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value=MedicineState.form_data.get(
                                        "purchase_price", ""
                                    ).to_string(),
                                    name="purchase_price",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Sale Price", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value=MedicineState.form_data.get(
                                        "sale_price", ""
                                    ).to_string(),
                                    name="sale_price",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Supplier", class_name="text-sm font-medium"
                                ),
                                rx.el.select(
                                    rx.foreach(
                                        MedicineState.suppliers,
                                        lambda s: rx.el.option(
                                            s["name"], value=s["id"].to_string()
                                        ),
                                    ),
                                    default_value=MedicineState.form_data.get(
                                        "supplier_id", ""
                                    ).to_string(),
                                    name="supplier_id",
                                    placeholder="Select a supplier",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="col-span-1",
                            ),
                            class_name="grid grid-cols-2 gap-4 py-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=MedicineState.toggle_form,
                                class_name="px-4 py-2 bg-gray-200 rounded-md text-gray-700 hover:bg-gray-300",
                            ),
                            rx.el.button(
                                "Save",
                                type="submit",
                                class_name="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                            ),
                            class_name="flex justify-end gap-3 pt-4 border-t",
                        ),
                        on_submit=MedicineState.save_medicine,
                    ),
                    class_name="bg-white rounded-xl shadow-lg w-full max-w-2xl p-6",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50",
            ),
        )
    )


def medicine_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Name", class_name="p-3 text-left"),
                    rx.el.th("Drug Type", class_name="p-3 text-left"),
                    rx.el.th("Batch No", class_name="p-3 text-left"),
                    rx.el.th("Expiry Date", class_name="p-3 text-left"),
                    rx.el.th("Quantity", class_name="p-3 text-left"),
                    rx.el.th("Unit", class_name="p-3 text-left"),
                    rx.el.th("Sale Price", class_name="p-3 text-left"),
                    rx.el.th("Supplier", class_name="p-3 text-left"),
                    rx.el.th("Actions", class_name="p-3 text-center"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    MedicineState.filtered_medicines,
                    lambda med: rx.el.tr(
                        rx.el.td(med["name"], class_name="p-3"),
                        rx.el.td(med["drug_type"], class_name="p-3"),
                        rx.el.td(med["batch_no"], class_name="p-3"),
                        rx.el.td(med["expiry_date"], class_name="p-3"),
                        rx.el.td(med["quantity"], class_name="p-3"),
                        rx.el.td(med["unit"], class_name="p-3"),
                        rx.el.td(f"{med['sale_price']:.2f}", class_name="p-3"),
                        rx.el.td(med["supplier_name"], class_name="p-3"),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-4 w-4"),
                                    on_click=lambda: MedicineState.open_edit_form(med),
                                    class_name="text-blue-500 hover:text-blue-700",
                                ),
                                rx.el.button(
                                    rx.icon("trash-2", class_name="h-4 w-4"),
                                    on_click=lambda: MedicineState.delete_medicine(
                                        med["id"]
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


def alerts_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Low Stock Alerts",
                class_name="text-lg font-semibold text-gray-800 mb-2",
            ),
            rx.foreach(
                MedicineState.low_stock_medicines,
                lambda med: rx.el.div(
                    rx.el.span(med["name"]),
                    rx.el.span(
                        f"{med['quantity']} {med['unit'] | ''}",
                        class_name="ml-auto text-sm font-bold text-yellow-600 bg-yellow-100 px-2 py-1 rounded-full",
                    ),
                    class_name="flex justify-between items-center p-2 border-b",
                ),
            ),
            class_name="bg-white border rounded-xl shadow-sm p-4",
        ),
        rx.el.div(
            rx.el.h3(
                "Expiry Alerts (Next 30 Days)",
                class_name="text-lg font-semibold text-gray-800 mb-2",
            ),
            rx.foreach(
                MedicineState.expiring_medicines,
                lambda med: rx.el.div(
                    rx.el.span(med["name"]),
                    rx.el.span(
                        f"Expires {med['expiry_date']}",
                        class_name="ml-auto text-sm font-bold text-red-600 bg-red-100 px-2 py-1 rounded-full",
                    ),
                    class_name="flex justify-between items-center p-2 border-b",
                ),
            ),
            class_name="bg-white border rounded-xl shadow-sm p-4",
        ),
        class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
    )


def medicines_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Manage Medicines", class_name="text-3xl font-bold text-gray-800"),
            rx.el.div(
                rx.el.input(
                    placeholder="Search by name or batch...",
                    on_change=MedicineState.set_search_query,
                    class_name="p-2 border rounded-md w-full md:w-1/3",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Medicine",
                    on_click=MedicineState.open_add_form,
                    class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
        ),
        alerts_section(),
        medicine_table(),
        medicine_form_modal(),
        class_name="p-6",
    )