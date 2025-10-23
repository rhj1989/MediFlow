import reflex as rx
from typing import TypedDict, Optional
from .db_state import get_db_connection
import datetime
import logging


class Customer(TypedDict):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    date_registered: str
    prescription_count: int


class CustomerState(rx.State):
    customers: list[Customer] = []
    search_query: str = ""
    show_form: bool = False
    is_editing: bool = False
    edit_id: Optional[int] = None
    form_data: dict = {}

    @rx.var
    def filtered_customers(self) -> list[Customer]:
        if not self.search_query:
            return self.customers
        query = self.search_query.lower()
        return [
            c
            for c in self.customers
            if query in c["name"].lower() or (c["phone"] and query in c["phone"])
        ]

    @rx.event
    def load_customers(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, COUNT(p.id) as prescription_count
                FROM customers c
                LEFT JOIN prescriptions p ON c.id = p.customer_id
                GROUP BY c.id
                ORDER BY c.name
            """)
            self.customers = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "address": row["address"],
                    "date_registered": row["date_registered"],
                    "prescription_count": row["prescription_count"],
                }
                for row in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Error loading customers: {e}")
            yield rx.toast.error("Failed to load customers.")

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
    def open_edit_form(self, customer: Customer):
        self.is_editing = True
        self.edit_id = customer["id"]
        self.form_data = {
            "name": customer["name"],
            "phone": customer["phone"],
            "email": customer["email"],
            "address": customer["address"],
        }
        self.show_form = True

    @rx.event
    def save_customer(self, form_data: dict):
        self.form_data = form_data
        name = form_data.get("name")
        if not name:
            return rx.toast.error("Customer name is required.")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.is_editing:
                cursor.execute(
                    "UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?",
                    (
                        name,
                        form_data.get("phone"),
                        form_data.get("email"),
                        form_data.get("address"),
                        self.edit_id,
                    ),
                )
                yield rx.toast.success("Customer updated successfully!")
            else:
                cursor.execute(
                    "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                    (
                        name,
                        form_data.get("phone"),
                        form_data.get("email"),
                        form_data.get("address"),
                    ),
                )
                yield rx.toast.success("Customer added successfully!")
            conn.commit()
            conn.close()
            self.toggle_form()
            return CustomerState.load_customers
        except Exception as e:
            logging.exception(f"Error saving customer: {e}")
            yield rx.toast.error(f"Failed to save customer: {e}")

    @rx.event
    def delete_customer(self, customer_id: int):
        try:
            conn = get_db_connection()
            count = conn.execute(
                "SELECT COUNT(*) FROM sales WHERE customer_id = ?", (customer_id,)
            ).fetchone()[0]
            if count > 0:
                yield rx.toast.error(
                    "Cannot delete customer with existing sales records."
                )
                conn.close()
                return
            conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            conn.close()
            yield rx.toast.info("Customer deleted.")
            return CustomerState.load_customers
        except Exception as e:
            logging.exception(f"Error deleting customer: {e}")
            yield rx.toast.error(f"Failed to delete customer: {e}")