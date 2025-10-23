import reflex as rx
from app.states.prescription_state import PrescriptionState, Prescription


def prescription_form_modal() -> rx.Component:
    return rx.el.div(
        rx.cond(
            PrescriptionState.show_form,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(
                                PrescriptionState.is_editing,
                                "Edit Prescription",
                                "Add New Prescription",
                            ),
                            class_name="text-lg font-semibold text-gray-800",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=PrescriptionState.toggle_form,
                            class_name="text-gray-500 hover:text-gray-800",
                        ),
                        class_name="flex justify-between items-center pb-4 border-b",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Customer", class_name="text-sm font-medium"
                                ),
                                rx.el.select(
                                    rx.foreach(
                                        PrescriptionState.customers,
                                        lambda c: rx.el.option(
                                            c["name"], value=c["id"].to_string()
                                        ),
                                    ),
                                    default_value=PrescriptionState.form_data.get(
                                        "customer_id", ""
                                    ).to_string(),
                                    name="customer_id",
                                    placeholder="Select a customer",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                    required=True,
                                ),
                                class_name="col-span-1 md:col-span-2",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Prescription No.", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=PrescriptionState.form_data.get(
                                        "prescription_number", ""
                                    ),
                                    name="prescription_number",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Doctor Name", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    default_value=PrescriptionState.form_data.get(
                                        "doctor_name", ""
                                    ),
                                    name="doctor_name",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Prescription Date",
                                    class_name="text-sm font-medium",
                                ),
                                rx.el.input(
                                    type="date",
                                    default_value=PrescriptionState.form_data.get(
                                        "prescription_date", ""
                                    ),
                                    name="prescription_date",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label("Notes", class_name="text-sm font-medium"),
                                rx.el.input(
                                    default_value=PrescriptionState.form_data.get(
                                        "notes", ""
                                    ),
                                    name="notes",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Prescription Image",
                                    class_name="text-sm font-medium",
                                ),
                                rx.upload.root(
                                    rx.el.button(
                                        rx.icon(
                                            "cloud_upload", class_name="h-4 w-4 mr-2"
                                        ),
                                        "Select File",
                                        type="button",
                                        class_name="flex items-center text-sm px-3 py-1.5 border rounded-md text-gray-600 hover:bg-gray-50",
                                    ),
                                    id="prescription_upload",
                                    accept={"image/*": []},
                                    on_drop=PrescriptionState.handle_upload(
                                        rx.upload_files(upload_id="prescription_upload")
                                    ),
                                ),
                                rx.cond(
                                    PrescriptionState.form_image_preview != "",
                                    rx.image(
                                        src=PrescriptionState.form_image_preview,
                                        class_name="mt-2 h-32 w-auto object-contain rounded-md border p-1",
                                    ),
                                ),
                                class_name="col-span-1 md:col-span-2",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 py-4",
                        ),
                        rx.el.div(
                            rx.el.label("Medicines", class_name="text-sm font-medium"),
                            rx.el.div(
                                rx.el.input(
                                    placeholder="Search and add medicines...",
                                    on_key_down=PrescriptionState.set_medicine_search_query,
                                    class_name="w-full p-2 border rounded-md",
                                    default_value=PrescriptionState.medicine_search_query,
                                ),
                                rx.cond(
                                    PrescriptionState.medicine_search_query != "",
                                    rx.el.div(
                                        rx.foreach(
                                            PrescriptionState.filtered_medicines_for_selection,
                                            lambda med: rx.el.div(
                                                rx.el.p(
                                                    f"{med['name']} ({med['batch_no']}) - Stock: {med['quantity']}"
                                                ),
                                                on_click=lambda: PrescriptionState.add_medicine_to_prescription(
                                                    med
                                                ),
                                                class_name="p-2 hover:bg-gray-100 cursor-pointer rounded-md",
                                            ),
                                        ),
                                        class_name="absolute top-full left-0 right-0 bg-white border rounded-b-md shadow-lg z-20 max-h-48 overflow-y-auto mt-1",
                                    ),
                                ),
                                class_name="relative z-10",
                            ),
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th(
                                                "Medicine", class_name="p-2 text-left"
                                            ),
                                            rx.el.th(
                                                "Quantity", class_name="p-2 text-left"
                                            ),
                                            rx.el.th(
                                                "Dosage", class_name="p-2 text-left"
                                            ),
                                            rx.el.th("", class_name="p-2"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            PrescriptionState.selected_medicines_list,
                                            lambda med: rx.el.tr(
                                                rx.el.td(med["name"], class_name="p-2"),
                                                rx.el.td(
                                                    rx.el.input(
                                                        type="number",
                                                        default_value=med[
                                                            "quantity"
                                                        ].to_string(),
                                                        on_change=lambda val: PrescriptionState.update_prescription_medicine(
                                                            med["medicine_id"],
                                                            "quantity",
                                                            val,
                                                        ),
                                                        class_name="w-20 p-1 border rounded-md text-center",
                                                    ),
                                                    class_name="p-2",
                                                ),
                                                rx.el.td(
                                                    rx.el.input(
                                                        placeholder="e.g., 1-0-1 after food",
                                                        default_value=med[
                                                            "dosage_instructions"
                                                        ],
                                                        on_change=lambda val: PrescriptionState.update_prescription_medicine(
                                                            med["medicine_id"],
                                                            "dosage_instructions",
                                                            val,
                                                        ),
                                                        class_name="w-full p-1 border rounded-md",
                                                    ),
                                                    class_name="p-2",
                                                ),
                                                rx.el.td(
                                                    rx.el.button(
                                                        rx.icon(
                                                            "x", class_name="h-4 w-4"
                                                        ),
                                                        on_click=lambda: PrescriptionState.remove_medicine_from_prescription(
                                                            med["medicine_id"]
                                                        ),
                                                        class_name="text-red-500 hover:text-red-700",
                                                    ),
                                                    class_name="p-2 text-center",
                                                ),
                                                class_name="border-b",
                                            ),
                                        )
                                    ),
                                    class_name="w-full text-sm mt-2",
                                ),
                                class_name="mt-2 max-h-60 overflow-y-auto",
                            ),
                            class_name="col-span-1 md:col-span-2 mt-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=PrescriptionState.toggle_form,
                                class_name="px-4 py-2 bg-gray-200 rounded-md text-gray-700 hover:bg-gray-300",
                            ),
                            rx.el.button(
                                "Save Prescription",
                                type="submit",
                                class_name="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                            ),
                            class_name="flex justify-end gap-3 pt-4 border-t",
                        ),
                        on_submit=PrescriptionState.save_prescription,
                    ),
                    class_name="bg-white rounded-xl shadow-lg w-full max-w-2xl p-6",
                ),
                class_name="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 overflow-y-auto p-4",
            ),
        )
    )


def prescription_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Customer", class_name="p-3 text-left"),
                    rx.el.th("Prescription #", class_name="p-3 text-left"),
                    rx.el.th("Doctor", class_name="p-3 text-left"),
                    rx.el.th("Date", class_name="p-3 text-left"),
                    rx.el.th("Actions", class_name="p-3 text-center"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    PrescriptionState.filtered_prescriptions,
                    lambda p: rx.el.tr(
                        rx.el.td(p["customer_name"], class_name="p-3"),
                        rx.el.td(p["prescription_number"], class_name="p-3"),
                        rx.el.td(p["doctor_name"], class_name="p-3"),
                        rx.el.td(p["prescription_date"], class_name="p-3"),
                        rx.el.td(
                            rx.el.div(
                                rx.el.button(
                                    rx.icon("pencil", class_name="h-4 w-4"),
                                    on_click=lambda: PrescriptionState.open_edit_form(
                                        p
                                    ),
                                    class_name="text-blue-500 hover:text-blue-700",
                                ),
                                rx.el.button(
                                    rx.icon("trash-2", class_name="h-4 w-4"),
                                    on_click=lambda: PrescriptionState.delete_prescription(
                                        p["id"]
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


def prescriptions_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Manage Prescriptions", class_name="text-3xl font-bold text-gray-800"
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Search by customer name or prescription number...",
                    on_change=PrescriptionState.set_search_query,
                    class_name="p-2 border rounded-md w-full md:w-1/3",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Prescription",
                    on_click=PrescriptionState.open_add_form,
                    class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600",
                ),
                class_name="flex justify-between items-center mb-6",
            ),
        ),
        prescription_table(),
        prescription_form_modal(),
        class_name="p-6",
    )