import reflex as rx
from app.states.purchase_state import PurchaseState


def purchases_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Record New Purchase", class_name="text-3xl font-bold text-gray-800 mb-6"
        ),
        rx.el.div(
            rx.el.form(
                rx.el.div(
                    rx.el.div(
                        rx.el.label("Supplier", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.foreach(
                                PurchaseState.suppliers,
                                lambda s: rx.el.option(
                                    s["name"], value=s["id"].to_string()
                                ),
                            ),
                            name="supplier_id",
                            placeholder="Select a supplier",
                            default_value=PurchaseState.form_data.get(
                                "supplier_id", ""
                            ).to_string(),
                            class_name="mt-1 w-full p-2 border rounded-md",
                            required=True,
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Medicine", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.foreach(
                                PurchaseState.medicines,
                                lambda m: rx.el.option(
                                    m["name"], value=m["id"].to_string()
                                ),
                            ),
                            name="medicine_id",
                            placeholder="Select a medicine",
                            on_change=lambda val: PurchaseState.set_form_data(
                                {"medicine_id": val}
                            ),
                            default_value=PurchaseState.form_data.get(
                                "medicine_id", ""
                            ).to_string(),
                            class_name="mt-1 w-full p-2 border rounded-md",
                            required=True,
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Quantity", class_name="text-sm font-medium"),
                        rx.el.div(
                            rx.el.input(
                                name="quantity",
                                type="number",
                                placeholder="Enter quantity",
                                default_value=PurchaseState.form_data.get(
                                    "quantity", ""
                                ).to_string(),
                                class_name="mt-1 w-full p-2 border rounded-md",
                                required=True,
                            ),
                            rx.cond(
                                PurchaseState.selected_medicine_unit != "",
                                rx.el.span(
                                    PurchaseState.selected_medicine_unit,
                                    class_name="absolute right-3 top-1/2 -translate-y-1/2 mt-0.5 text-sm text-gray-500",
                                ),
                            ),
                            class_name="relative",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Purchase Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="purchase_date",
                            type="date",
                            default_value=PurchaseState.form_data.get(
                                "purchase_date", ""
                            ),
                            class_name="mt-1 w-full p-2 border rounded-md",
                            required=True,
                        ),
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6",
                ),
                rx.cond(
                    PurchaseState.error_message != "",
                    rx.el.p(
                        PurchaseState.error_message,
                        class_name="text-red-500 text-sm mb-4",
                    ),
                ),
                rx.el.button(
                    rx.icon("save", class_name="h-4 w-4 mr-2"),
                    "Save Purchase",
                    type="submit",
                    class_name="flex items-center px-6 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                on_submit=PurchaseState.handle_submit,
            ),
            class_name="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-lg border",
        ),
        class_name="p-6",
    )