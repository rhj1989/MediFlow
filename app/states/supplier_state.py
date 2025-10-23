import reflex as rx
from typing import TypedDict, Optional
from .db_state import get_db_connection
import logging


class Supplier(TypedDict):
    id: int
    name: str
    contact_no: Optional[str]
    address: Optional[str]


class SupplierState(rx.State):
    suppliers: list[Supplier] = []
    search_query: str = ""
    show_form: bool = False
    is_editing: bool = False
    edit_id: Optional[int] = None
    form_data: dict = {}

    @rx.var
    def filtered_suppliers(self) -> list[Supplier]:
        if not self.search_query:
            return self.suppliers
        query = self.search_query.lower()
        return [s for s in self.suppliers if query in s["name"].lower()]

    @rx.event
    def load_suppliers(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        self.suppliers = [
            {
                "id": row["id"],
                "name": row["name"],
                "contact_no": row["contact_no"],
                "address": row["address"],
            }
            for row in cursor.fetchall()
        ]
        conn.close()

    @rx.event
    def toggle_form(self):
        self.show_form = not self.show_form
        if not self.show_form:
            self.reset_form()

    @rx.event
    def reset_form(self):
        self.form_data = {}
        self.is_editing = False
        self.edit_id = None

    @rx.event
    def open_add_form(self):
        self.reset_form()
        self.show_form = True

    @rx.event
    def open_edit_form(self, supplier: Supplier):
        self.is_editing = True
        self.edit_id = supplier["id"]
        self.form_data = {
            "name": supplier["name"],
            "contact_no": supplier["contact_no"],
            "address": supplier["address"],
        }
        self.show_form = True

    @rx.event
    def handle_form_change(self, field: str, value: str):
        self.form_data[field] = value

    @rx.event
    def save_supplier(self, form_data: dict):
        self.form_data = form_data
        data = self.form_data
        if not data.get("name"):
            return rx.toast.error("Supplier name is required.")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.is_editing:
                cursor.execute(
                    "UPDATE suppliers SET name=?, contact_no=?, address=? WHERE id=?",
                    (
                        data["name"],
                        data.get("contact_no"),
                        data.get("address"),
                        self.edit_id,
                    ),
                )
                yield rx.toast.success("Supplier updated successfully!")
            else:
                cursor.execute(
                    "INSERT INTO suppliers (name, contact_no, address) VALUES (?, ?, ?)",
                    (data["name"], data.get("contact_no"), data.get("address")),
                )
                yield rx.toast.success("Supplier added successfully!")
            conn.commit()
            conn.close()
            self.toggle_form()
            return SupplierState.load_suppliers
        except Exception as e:
            logging.exception(e)
            yield rx.toast.error(f"Failed to save supplier: {e}")

    @rx.event
    def delete_supplier(self, supplier_id: int):
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            conn.commit()
            conn.close()
            yield rx.toast.info("Supplier deleted.")
            return SupplierState.load_suppliers
        except Exception as e:
            logging.exception(e)
            yield rx.toast.error(f"Failed to delete supplier: {e}")