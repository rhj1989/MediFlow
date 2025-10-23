import reflex as rx
from typing import TypedDict, Optional
from .db_state import get_db_connection
import datetime
import logging
import os


class Prescription(TypedDict):
    id: int
    customer_id: int
    customer_name: str
    prescription_number: Optional[str]
    doctor_name: Optional[str]
    prescription_date: str
    notes: Optional[str]
    image_path: Optional[str]


class Customer(TypedDict):
    id: int
    name: str


class MedicineBasic(TypedDict):
    id: int
    name: str
    batch_no: str
    quantity: int
    unit: Optional[str]


class PrescriptionMedicine(TypedDict):
    medicine_id: int
    name: str
    quantity: int
    dosage_instructions: str


class PrescriptionState(rx.State):
    prescriptions: list[Prescription] = []
    customers: list[Customer] = []
    medicines_for_selection: list[MedicineBasic] = []
    search_query: str = ""
    medicine_search_query: str = ""
    show_form: bool = False
    is_editing: bool = False
    edit_id: Optional[int] = None
    form_data: dict = {}
    selected_medicines: dict[int, PrescriptionMedicine] = {}

    def _get_prescriptions_dir(self) -> str:
        return os.path.join(rx.get_upload_dir(), "prescriptions")

    @rx.var
    def filtered_prescriptions(self) -> list[Prescription]:
        query = self.search_query.lower()
        if not query:
            return self.prescriptions
        return [
            p
            for p in self.prescriptions
            if query in p["customer_name"].lower()
            or (p["prescription_number"] and query in p["prescription_number"].lower())
        ]

    @rx.var
    def filtered_medicines_for_selection(self) -> list[MedicineBasic]:
        if not self.medicine_search_query:
            return []
        query = self.medicine_search_query.lower()
        return [
            m
            for m in self.medicines_for_selection
            if query in m["name"].lower() or query in m["batch_no"].lower()
        ][:10]

    @rx.var
    def selected_medicines_list(self) -> list[PrescriptionMedicine]:
        return list(self.selected_medicines.values())

    @rx.var
    def form_image_preview(self) -> str:
        image_path = self.form_data.get("image_path")
        if image_path:
            return f"/prescriptions/{image_path}"
        return ""

    @rx.event
    def load_prescriptions(self):
        customer_id_param = self.router.page.params.get("customer_id")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            base_query = """
                SELECT p.*, c.name as customer_name 
                FROM prescriptions p
                JOIN customers c ON p.customer_id = c.id
            """
            params = ()
            if customer_id_param:
                base_query += " WHERE p.customer_id = ?"
                params = (customer_id_param,)
            base_query += " ORDER BY p.prescription_date DESC"
            cursor.execute(base_query, params)
            self.prescriptions = [
                {
                    "id": r["id"],
                    "customer_id": r["customer_id"],
                    "customer_name": r["customer_name"],
                    "prescription_number": r["prescription_number"],
                    "doctor_name": r["doctor_name"],
                    "prescription_date": r["prescription_date"],
                    "notes": r["notes"],
                    "image_path": r["image_path"],
                }
                for r in cursor.fetchall()
            ]
            cursor.execute("SELECT id, name FROM customers ORDER BY name")
            self.customers = [
                {"id": r["id"], "name": r["name"]} for r in cursor.fetchall()
            ]
            cursor.execute(
                "SELECT id, name, batch_no, quantity, unit FROM medicines WHERE quantity > 0 ORDER BY name"
            )
            self.medicines_for_selection = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "batch_no": r["batch_no"],
                    "quantity": r["quantity"],
                    "unit": r["unit"],
                }
                for r in cursor.fetchall()
            ]
            conn.close()
        except Exception as e:
            logging.exception(f"Error loading prescriptions: {e}")

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
        self.form_image_preview = ""
        self.selected_medicines = {}
        self.medicine_search_query = ""

    @rx.event
    def open_add_form(self):
        self.reset_form()
        self.form_data = {
            "prescription_date": datetime.date.today().strftime("%Y-%m-%d")
        }
        self.show_form = True

    @rx.event
    def open_edit_form(self, prescription: Prescription):
        self.reset_form()
        self.is_editing = True
        self.edit_id = prescription["id"]
        self.form_data = {
            "customer_id": str(prescription["customer_id"]),
            "prescription_number": prescription["prescription_number"],
            "doctor_name": prescription["doctor_name"],
            "prescription_date": prescription["prescription_date"],
            "notes": prescription["notes"],
            "image_path": prescription["image_path"],
        }
        self.show_form = True
        return PrescriptionState.load_prescription_medicines

    @rx.event
    def load_prescription_medicines(self):
        if not self.edit_id:
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT pm.medicine_id, m.name, pm.quantity, pm.dosage_instructions
                FROM prescription_medicines pm
                JOIN medicines m ON pm.medicine_id = m.id
                WHERE pm.prescription_id = ?
            """,
                (self.edit_id,),
            )
            self.selected_medicines = {
                r["medicine_id"]: {
                    "medicine_id": r["medicine_id"],
                    "name": r["name"],
                    "quantity": r["quantity"],
                    "dosage_instructions": r["dosage_instructions"],
                }
                for r in cursor.fetchall()
            }
            conn.close()
        except Exception as e:
            logging.exception(f"Error loading prescription medicines: {e}")

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        upload_dir = self._get_prescriptions_dir()
        os.makedirs(upload_dir, exist_ok=True)
        unique_name = f"{datetime.datetime.now().timestamp()}_{file.name}"
        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(upload_data)
        self.form_data["image_path"] = unique_name

    @rx.event
    def add_medicine_to_prescription(self, medicine: MedicineBasic):
        med_id = medicine["id"]
        if med_id not in self.selected_medicines:
            self.selected_medicines[med_id] = {
                "medicine_id": med_id,
                "name": medicine["name"],
                "quantity": 1,
                "dosage_instructions": "",
            }
        self.medicine_search_query = ""

    @rx.event
    def update_prescription_medicine(self, med_id: int, field: str, value: str):
        if med_id in self.selected_medicines:
            if field == "quantity":
                try:
                    self.selected_medicines[med_id]["quantity"] = int(value)
                except ValueError as e:
                    logging.exception(
                        f"Error updating prescription medicine quantity: {e}"
                    )
            else:
                self.selected_medicines[med_id][field] = value

    @rx.event
    def remove_medicine_from_prescription(self, med_id: int):
        if med_id in self.selected_medicines:
            del self.selected_medicines[med_id]

    @rx.event
    def save_prescription(self, form_data: dict):
        if not form_data.get("customer_id"):
            return rx.toast.error("Customer is required.")
        merged_data = {**self.form_data, **form_data}
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            image_path_to_save = merged_data.get("image_path")
            if self.is_editing:
                prescription_id = self.edit_id
                if not image_path_to_save:
                    cursor.execute(
                        "SELECT image_path FROM prescriptions WHERE id = ?",
                        (self.edit_id,),
                    )
                    image_path_to_save = cursor.fetchone()["image_path"]
                cursor.execute(
                    """UPDATE prescriptions SET customer_id=?, prescription_number=?, doctor_name=?, 
                       prescription_date=?, notes=?, image_path=? WHERE id=?""",
                    (
                        int(merged_data["customer_id"]),
                        merged_data.get("prescription_number"),
                        merged_data.get("doctor_name"),
                        merged_data.get("prescription_date"),
                        merged_data.get("notes"),
                        image_path_to_save,
                        self.edit_id,
                    ),
                )
            else:
                cursor.execute(
                    """INSERT INTO prescriptions (customer_id, prescription_number, doctor_name, prescription_date, notes, image_path) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        int(merged_data["customer_id"]),
                        merged_data.get("prescription_number"),
                        merged_data.get("doctor_name"),
                        merged_data.get("prescription_date"),
                        merged_data.get("notes"),
                        image_path_to_save,
                    ),
                )
                prescription_id = cursor.lastrowid
            cursor.execute(
                "DELETE FROM prescription_medicines WHERE prescription_id = ?",
                (prescription_id,),
            )
            for med in self.selected_medicines.values():
                cursor.execute(
                    """
                    INSERT INTO prescription_medicines (prescription_id, medicine_id, quantity, dosage_instructions)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        prescription_id,
                        med["medicine_id"],
                        med["quantity"],
                        med["dosage_instructions"],
                    ),
                )
            conn.commit()
            if self.is_editing:
                yield rx.toast.success("Prescription updated successfully!")
            else:
                yield rx.toast.success("Prescription added successfully!")
            conn.close()
            self.toggle_form()
            return PrescriptionState.load_prescriptions
        except Exception as e:
            logging.exception(f"Error saving prescription: {e}")
            yield rx.toast.error(f"Failed to save prescription: {e}")

    @rx.event
    def delete_prescription(self, prescription_id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT image_path FROM prescriptions WHERE id = ?", (prescription_id,)
            )
            result = cursor.fetchone()
            if result and result["image_path"]:
                image_path = os.path.join(
                    self._get_prescriptions_dir(), result["image_path"]
                )
                if os.path.exists(image_path):
                    os.remove(image_path)
            cursor.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
            conn.commit()
            conn.close()
            yield rx.toast.info("Prescription deleted.")
            return PrescriptionState.load_prescriptions
        except Exception as e:
            logging.exception(f"Error deleting prescription: {e}")
            yield rx.toast.error(f"Failed to delete prescription: {e}")