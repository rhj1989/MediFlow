import reflex as rx
import logging
import shutil
from .db_state import DATABASE_URL


class SettingsState(rx.State):
    @rx.event
    def backup_database(self):
        try:
            with open(DATABASE_URL, "rb") as f:
                db_data = f.read()
            return rx.download(data=db_data, filename="mediflow_backup.db")
        except Exception as e:
            logging.exception(f"Error creating database backup: {e}")
            return rx.toast.error("Failed to create backup.")

    @rx.event
    async def restore_database(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.warning("Please select a database file to restore.")
            return
        file = files[0]
        try:
            upload_data = await file.read()
            with open(DATABASE_URL, "wb") as f:
                f.write(upload_data)
            yield rx.toast.success(
                "Database restored successfully! The app will now reload."
            )
        except Exception as e:
            logging.exception(f"Error restoring database: {e}")
            yield rx.toast.error(f"Failed to restore database: {e}")