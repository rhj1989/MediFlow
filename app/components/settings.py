import reflex as rx
from app.states.settings_state import SettingsState


def settings_card(
    title: str, description: str, button_component: rx.Component
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="text-lg font-semibold text-gray-800"),
            rx.el.p(description, class_name="text-sm text-gray-500 mt-1"),
            class_name="flex-1",
        ),
        button_component,
        class_name="flex items-center justify-between p-6 bg-white border rounded-xl shadow-sm",
    )


def settings_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1("Settings", class_name="text-3xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            settings_card(
                "Database Backup",
                "Download a backup of the entire application database.",
                rx.el.button(
                    rx.icon("database-backup", class_name="h-4 w-4 mr-2"),
                    "Backup Now",
                    on_click=SettingsState.backup_database,
                    class_name="flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600",
                ),
            ),
            settings_card(
                "Database Restore",
                "Restore the database from a backup file. This will overwrite all current data.",
                rx.upload.root(
                    rx.el.button(
                        rx.icon("cloud_upload", class_name="h-4 w-4 mr-2"),
                        "Select File to Restore...",
                        class_name="flex items-center px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600",
                    ),
                    id="db_restore",
                    on_drop=SettingsState.restore_database(
                        rx.upload_files(upload_id="db_restore")
                    ),
                    accept={".db": ["application/octet-stream"]},
                ),
            ),
            class_name="grid grid-cols-1 gap-6",
        ),
        class_name="p-6",
    )