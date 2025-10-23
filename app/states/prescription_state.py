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


class PrescriptionState(rx.State):
    prescriptions: list[Prescription] = []
    customers: list[Customer] = []
    search_query: str = ""
    show_form: bool = False
    is_editing: bool = False
    edit_id: Optional[int] = None
    form_data: dict = {}
    form_image_preview: str = ""

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
        }
        if prescription["image_path"]:
            self.form_image_preview = (
                f"/upload/prescriptions/{prescription['image_path']}"
            )
        self.show_form = True

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
        self.form_image_preview = f"/upload/prescriptions/{unique_name}"

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
                yield rx.toast.success("Prescription updated successfully!")
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
                yield rx.toast.success("Prescription added successfully!")
            conn.commit()
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