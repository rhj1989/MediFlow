import reflex as rx
from typing import TypedDict, Optional
from .db_state import get_db_connection
import datetime
import logging


class Medicine(TypedDict):
    id: int
    name: str
    batch_no: str
    expiry_date: str
    quantity: int
    purchase_price: float
    sale_price: float
    supplier_id: Optional[int]
    supplier_name: Optional[str]
    unit: Optional[str]
    drug_type: Optional[str]


class Supplier(TypedDict):
    id: int
    name: str


class MedicineState(rx.State):
    medicines: list[Medicine] = []
    suppliers: list[Supplier] = []
    search_query: str = ""
    show_form: bool = False
    is_editing: bool = False
    edit_id: Optional[int] = None
    form_data: dict = {}
    drug_types: list[str] = [
        "Tablet",
        "Capsule",
        "Syrup",
        "Injection",
        "Cream",
        "Ointment",
        "Drops",
        "Inhaler",
    ]
    medicine_units: list[str] = [
        "Tablets",
        "Bottles",
        "Strips",
        "ml",
        "mg",
        "gm",
        "Injections",
        "Syrups",
    ]

    @rx.var
    def filtered_medicines(self) -> list[Medicine]:
        if not self.search_query:
            return self.medicines
        query = self.search_query.lower()
        return [
            m
            for m in self.medicines
            if query in m["name"].lower() or query in m["batch_no"].lower()
        ]

    @rx.var
    def low_stock_medicines(self) -> list[Medicine]:
        return [m for m in self.medicines if m["quantity"] < 10]

    @rx.var
    def expiring_medicines(self) -> list[Medicine]:
        today = datetime.date.today()
        thirty_days = today + datetime.timedelta(days=30)
        return [
            m
            for m in self.medicines
            if datetime.datetime.strptime(m["expiry_date"], "%Y-%m-%d").date()
            <= thirty_days
        ]

    @rx.event
    def load_medicines(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, s.name as supplier_name 
            FROM medicines m 
            LEFT JOIN suppliers s ON m.supplier_id = s.id
        """)
        self.medicines = [
            {
                "id": row["id"],
                "name": row["name"],
                "batch_no": row["batch_no"],
                "expiry_date": row["expiry_date"],
                "quantity": row["quantity"],
                "purchase_price": row["purchase_price"],
                "sale_price": row["sale_price"],
                "supplier_id": row["supplier_id"],
                "supplier_name": row["supplier_name"],
                "unit": row["unit"],
                "drug_type": row["drug_type"],
            }
            for row in cursor.fetchall()
        ]
        cursor.execute("SELECT id, name FROM suppliers")
        self.suppliers = [
            {"id": row["id"], "name": row["name"]} for row in cursor.fetchall()
        ]
        conn.close()

    @rx.event
    def toggle_form(self):
        self.show_form = not self.show_form
        if not self.show_form:
            self.reset_form()

    def _reset_form_fields(self):
        self.form_data = {}
        self.is_editing = False
        self.edit_id = None

    @rx.event
    def reset_form(self):
        self._reset_form_fields()

    @rx.event
    def open_add_form(self):
        self.reset_form()
        self.show_form = True

    @rx.event
    def open_edit_form(self, medicine: Medicine):
        self.is_editing = True
        self.edit_id = medicine["id"]
        self.form_data = {
            "name": medicine["name"],
            "batch_no": medicine["batch_no"],
            "expiry_date": medicine["expiry_date"],
            "quantity": medicine["quantity"],
            "purchase_price": medicine["purchase_price"],
            "sale_price": medicine["sale_price"],
            "unit": medicine["unit"],
            "drug_type": medicine["drug_type"],
            "supplier_id": str(medicine["supplier_id"])
            if medicine["supplier_id"]
            else "",
        }
        self.show_form = True

    @rx.event
    def handle_form_change(self, field: str, value: str):
        self.form_data[field] = value

    @rx.event
    def save_medicine(self, form_data: dict):
        self.form_data = form_data
        data = self.form_data
        required_fields = [
            "name",
            "batch_no",
            "expiry_date",
            "quantity",
            "purchase_price",
            "sale_price",
        ]
        for field in required_fields:
            if not data.get(field):
                return rx.toast.error(
                    f"{field.replace('_', ' ').capitalize()} is required."
                )
        try:
            quantity = int(data["quantity"])
            purchase_price = float(data["purchase_price"])
            sale_price = float(data["sale_price"])
            supplier_id_str = data.get("supplier_id", "")
            supplier_id = int(supplier_id_str) if supplier_id_str else None
        except (ValueError, TypeError) as e:
            logging.exception(e)
            return rx.toast.error("Quantity and prices must be valid numbers.")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.is_editing:
                cursor.execute(
                    """UPDATE medicines SET name=?, batch_no=?, expiry_date=?, quantity=?, 
                       purchase_price=?, sale_price=?, supplier_id=?, unit=?, drug_type=? WHERE id=?""",
                    (
                        data["name"],
                        data["batch_no"],
                        data["expiry_date"],
                        quantity,
                        purchase_price,
                        sale_price,
                        supplier_id,
                        data.get("unit"),
                        data.get("drug_type"),
                        self.edit_id,
                    ),
                )
                yield rx.toast.success("Medicine updated successfully!")
            else:
                cursor.execute(
                    """INSERT INTO medicines (name, batch_no, expiry_date, quantity, purchase_price, sale_price, supplier_id, unit, drug_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        data["name"],
                        data["batch_no"],
                        data["expiry_date"],
                        quantity,
                        purchase_price,
                        sale_price,
                        supplier_id,
                        data.get("unit"),
                        data.get("drug_type"),
                    ),
                )
                yield rx.toast.success("Medicine added successfully!")
            conn.commit()
            conn.close()
            self.toggle_form()
            return MedicineState.load_medicines
        except Exception as e:
            logging.exception(e)
            yield rx.toast.error(f"Failed to save medicine: {e}")

    @rx.event
    def delete_medicine(self, medicine_id: int):
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
            conn.commit()
            conn.close()
            yield rx.toast.info("Medicine deleted.")
            return MedicineState.load_medicines
        except Exception as e:
            logging.exception(e)
            yield rx.toast.error(f"Failed to delete medicine: {e}")