import reflex as rx
from typing import Optional
import sqlite3
from .db_state import get_db_connection


class AuthState(rx.State):
    is_authenticated: bool = False
    username: str = ""
    error_message: str = ""
    token: Optional[str] = rx.Cookie(name="token")

    def _validate_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (token,)
        ).fetchone()
        conn.close()
        return user is not None

    @rx.event
    def on_load(self):
        if self.token and self._validate_token(self.token):
            self.is_authenticated = True
            self.username = self.token
        else:
            self.is_authenticated = False
            self.username = ""
            self.token = None
            return rx.redirect("/login")

    @rx.event
    def login(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()
        if user:
            self.is_authenticated = True
            self.username = username
            self.token = username
            self.error_message = ""
            return rx.redirect("/")
        else:
            self.error_message = "Invalid username or password"

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.username = ""
        self.token = None
        return rx.redirect("/login")