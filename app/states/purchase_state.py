import reflex as rx
from typing import TypedDict, Optional
import datetime
import logging
from .db_state import get_db_connection


class Supplier(TypedDict):
    id: int
    name: str


class MedicineBasic(TypedDict):
    id: int
    name: str
    unit: Optional[str]


class PurchaseState(rx.State):
    suppliers: list[Supplier] = []
    medicines: list[MedicineBasic] = []
    form_data: dict = {"purchase_date": datetime.date.today().strftime("%Y-%m-%d")}
    error_message: str = ""

    @rx.var
    def selected_medicine_unit(self) -> str:
        med_id = self.form_data.get("medicine_id")
        if med_id:
            try:
                selected_med_id = int(med_id)
                for med in self.medicines:
                    if med["id"] == selected_med_id:
                        return med.get("unit", "") or ""
            except (ValueError, TypeError) as e:
                logging.exception(f"Error processing selected medicine unit: {e}")
                return ""
        return ""

    @rx.event
    def load_dependencies(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM suppliers ORDER BY name")
            self.suppliers = [
                {"id": r["id"], "name": r["name"]} for r in cursor.fetchall()
            ]
            cursor.execute("SELECT id, name, unit FROM medicines ORDER BY name")
            self.medicines = [
                {"id": r["id"], "name": r["name"], "unit": r["unit"]}
                for r in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Failed to load dependencies for purchases: {e}")

    @rx.event
    def handle_submit(self, form_data: dict):
        self.form_data = form_data
        self.error_message = ""
        supplier_id = self.form_data.get("supplier_id")
        medicine_id = self.form_data.get("medicine_id")
        quantity_str = self.form_data.get("quantity")
        purchase_date = self.form_data.get("purchase_date")
        required_fields = {
            "supplier_id": "Supplier",
            "medicine_id": "Medicine",
            "quantity": "Quantity",
            "purchase_date": "Purchase Date",
        }
        for field_key, field_name in required_fields.items():
            if not self.form_data.get(field_key):
                self.error_message = f"{field_name} is required."
                return
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                self.error_message = "Quantity must be a positive number."
                return
        except (ValueError, TypeError) as e:
            logging.exception(e)
            self.error_message = "Quantity must be a valid number."
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO purchases (supplier_id, medicine_id, quantity, purchase_date) VALUES (?, ?, ?, ?)",
                (int(supplier_id), int(medicine_id), quantity, purchase_date),
            )
            cursor.execute(
                "UPDATE medicines SET quantity = quantity + ? WHERE id = ?",
                (quantity, int(medicine_id)),
            )
            conn.commit()
            conn.close()
            yield rx.toast.success("Purchase recorded and stock updated!")
            self.form_data = {
                "purchase_date": datetime.date.today().strftime("%Y-%m-%d")
            }
        except Exception as e:
            logging.exception(f"Error recording purchase: {e}")
            self.error_message = f"Database error: {e}"
            yield rx.toast.error("Failed to record purchase.")