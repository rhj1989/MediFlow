import reflex as rx
from typing import TypedDict, Optional
import datetime
import logging
from .db_state import get_db_connection


class MedicineSearchResult(TypedDict):
    id: int
    name: str
    batch_no: str
    sale_price: float
    quantity: int
    unit: Optional[str]


class CartItem(TypedDict):
    id: int
    name: str
    batch_no: str
    sale_price: float
    quantity: int
    available_quantity: int
    subtotal: float
    unit: Optional[str]


class Customer(TypedDict):
    id: int
    name: str


class PrescriptionSummary(TypedDict):
    id: int
    display_text: str


class BillingState(rx.State):
    search_query: str = ""
    search_results: list[MedicineSearchResult] = []
    cart: dict[int, CartItem] = {}
    customers: list[Customer] = []
    selected_customer_id: str = ""
    doctor_name: str = ""
    customer_prescriptions: list[PrescriptionSummary] = []
    selected_prescription_id: str = ""

    @rx.var
    def cart_items(self) -> list[CartItem]:
        return list(self.cart.values())

    @rx.var
    def total_amount(self) -> float:
        return sum((item["subtotal"] for item in self.cart.values()))

    @rx.event
    def on_load(self):
        self.search_query = ""
        self.search_results = []
        self.cart = {}
        self.selected_customer_id = ""
        self.doctor_name = ""
        self.customer_prescriptions = []
        self.selected_prescription_id = ""
        return BillingState.load_customers

    @rx.event
    def set_selected_customer_id(self, customer_id: str):
        self.selected_customer_id = customer_id
        self.customer_prescriptions = []
        self.selected_prescription_id = ""
        if customer_id:
            return BillingState.load_customer_prescriptions

    @rx.event
    def load_customer_prescriptions(self):
        if not self.selected_customer_id:
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, prescription_date, doctor_name, prescription_number 
                FROM prescriptions WHERE customer_id = ? ORDER BY prescription_date DESC
            """,
                (int(self.selected_customer_id),),
            )
            self.customer_prescriptions = [
                {
                    "id": r["id"],
                    "display_text": f"#{r['prescription_number'] or r['id']} - {r['doctor_name'] or 'N/A'} ({r['prescription_date']})",
                }
                for r in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Error loading customer prescriptions: {e}")

    @rx.event
    def load_customers(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM customers ORDER BY name")
            self.customers = [
                {"id": row["id"], "name": row["name"]} for row in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Error loading customers in billing: {e}")

    @rx.event
    def search_medicines(self, query: str):
        self.search_query = query
        if not query:
            self.search_results = []
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, batch_no, sale_price, quantity, unit FROM medicines WHERE (name LIKE ? OR batch_no LIKE ?) AND quantity > 0 LIMIT 10",
                (f"%{query}%", f"%{query}%"),
            )
            self.search_results = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "batch_no": row["batch_no"],
                    "sale_price": row["sale_price"],
                    "quantity": row["quantity"],
                    "unit": row["unit"],
                }
                for row in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Error searching medicines: {e}")
            self.search_results = []

    @rx.event
    def add_to_cart(self, medicine: MedicineSearchResult):
        med_id = medicine["id"]
        if med_id in self.cart:
            self.update_cart_quantity(med_id, self.cart[med_id]["quantity"] + 1)
        else:
            self.cart[med_id] = {
                "id": med_id,
                "name": medicine["name"],
                "batch_no": medicine["batch_no"],
                "sale_price": medicine["sale_price"],
                "quantity": 1,
                "available_quantity": medicine["quantity"],
                "subtotal": medicine["sale_price"],
                "unit": medicine["unit"],
            }
        self.search_query = ""
        self.search_results = []

    @rx.event
    def update_cart_quantity(self, med_id: int, quantity_str: str):
        try:
            quantity = int(quantity_str)
            if med_id in self.cart:
                item = self.cart[med_id]
                if 0 < quantity <= item["available_quantity"]:
                    item["quantity"] = quantity
                    item["subtotal"] = item["sale_price"] * quantity
                    self.cart = self.cart
                else:
                    yield rx.toast.warning("Quantity exceeds available stock.")
        except ValueError as e:
            logging.exception(f"Error updating cart quantity: {e}")
            pass

    @rx.event
    def remove_from_cart(self, med_id: int):
        if med_id in self.cart:
            del self.cart[med_id]
            self.cart = self.cart

    @rx.event
    def load_prescription_into_cart(self, prescription_id: str):
        self.selected_prescription_id = prescription_id
        if not prescription_id:
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT pm.medicine_id, m.name, m.batch_no, m.sale_price, m.quantity as available_quantity, m.unit, pm.quantity as prescription_qty
                FROM prescription_medicines pm
                JOIN medicines m ON pm.medicine_id = m.id
                WHERE pm.prescription_id = ?
            """,
                (int(prescription_id),),
            )
            medicines_to_add = cursor.fetchall()
            conn.close()
            for med in medicines_to_add:
                med_id = med["medicine_id"]
                quantity_to_add = med["prescription_qty"]
                if med["available_quantity"] < quantity_to_add:
                    yield rx.toast.warning(
                        f"Stock for {med['name']} is low. Adding available quantity."
                    )
                    quantity_to_add = med["available_quantity"]
                if quantity_to_add > 0:
                    if med_id in self.cart:
                        self.cart[med_id]["quantity"] += quantity_to_add
                        self.cart[med_id]["subtotal"] = (
                            self.cart[med_id]["quantity"]
                            * self.cart[med_id]["sale_price"]
                        )
                    else:
                        self.cart[med_id] = {
                            "id": med_id,
                            "name": med["name"],
                            "batch_no": med["batch_no"],
                            "sale_price": med["sale_price"],
                            "quantity": quantity_to_add,
                            "available_quantity": med["available_quantity"],
                            "subtotal": med["sale_price"] * quantity_to_add,
                            "unit": med["unit"],
                        }
            self.cart = self.cart
        except Exception as e:
            logging.exception(f"Error loading prescription into cart: {e}")
            yield rx.toast.error("Failed to load prescription medicines.")

    @rx.event
    def generate_bill(self):
        if not self.cart:
            return rx.toast.error("Cart is empty.")
        try:
            customer_id = (
                int(self.selected_customer_id) if self.selected_customer_id else None
            )
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sales (total_amount, customer_id, doctor_name) VALUES (?, ?, ?)",
                (self.total_amount, customer_id, self.doctor_name),
            )
            sale_id = cursor.lastrowid
            for item in self.cart.values():
                cursor.execute(
                    "INSERT INTO sale_items (sale_id, medicine_id, quantity, price_per_unit) VALUES (?, ?, ?, ?)",
                    (sale_id, item["id"], item["quantity"], item["sale_price"]),
                )
                cursor.execute(
                    "UPDATE medicines SET quantity = quantity - ? WHERE id = ?",
                    (item["quantity"], item["id"]),
                )
            conn.commit()
            conn.close()
            yield rx.toast.success(f"Bill #{sale_id} generated successfully!")
            self._clear_bill()
        except Exception as e:
            logging.exception(f"Error generating bill: {e}")
            yield rx.toast.error(f"Failed to generate bill: {e}")

    def _clear_bill(self):
        self.cart = {}
        self.selected_customer_id = ""
        self.search_query = ""
        self.search_results = []
        self.doctor_name = ""
        self.customer_prescriptions = []
        self.selected_prescription_id = ""

    @rx.event
    def clear_bill_event(self):
        self._clear_bill()