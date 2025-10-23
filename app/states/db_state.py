import reflex as rx
import sqlite3
import datetime
from typing import Any, Optional

DATABASE_URL = "medical_store.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            quantity INTEGER NOT NULL,
            purchase_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            supplier_id INTEGER,
            unit TEXT,
            drug_type TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)
    cursor.execute("PRAGMA table_info(medicines)")
    columns = [column[1] for column in cursor.fetchall()]
    if "unit" not in columns:
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN unit TEXT")
        except sqlite3.OperationalError as e:
            import logging

            logging.exception(f"Error adding unit column: {e}")
    if "drug_type" not in columns:
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN drug_type TEXT")
        except sqlite3.OperationalError as e:
            import logging

            logging.exception(f"Error adding drug_type column: {e}")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_no TEXT,
            address TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            purchase_date DATE NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            doctor_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            prescription_number TEXT,
            doctor_name TEXT,
            prescription_date DATE,
            notes TEXT,
            image_path TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    try:
        cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in cursor.fetchall()]
        if "customer_id" not in columns:
            cursor.execute(
                "ALTER TABLE sales ADD COLUMN customer_id INTEGER REFERENCES customers(id)"
            )
        if "doctor_name" not in columns:
            cursor.execute("ALTER TABLE sales ADD COLUMN doctor_name TEXT")
    except sqlite3.OperationalError as e:
        import logging

        logging.exception(f"Error adding customer_id column to sales: {e}")
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin")
        )
    conn.commit()
    conn.close()


class DBState(rx.State):
    @rx.var
    def total_customers(self) -> int:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        conn.close()
        return count

    @rx.var
    def total_medicines(self) -> int:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
        conn.close()
        return count

    @rx.var
    def low_stock_items(self) -> int:
        conn = get_db_connection()
        count = conn.execute(
            "SELECT COUNT(*) FROM medicines WHERE quantity < 10"
        ).fetchone()[0]
        conn.close()
        return count

    @rx.var
    def todays_sales(self) -> float:
        conn = get_db_connection()
        today = datetime.date.today()
        total = conn.execute(
            "SELECT SUM(total_amount) FROM sales WHERE DATE(sale_date) = ?", (today,)
        ).fetchone()[0]
        conn.close()
        return total or 0.0

    @rx.var
    def expiry_alerts(self) -> int:
        conn = get_db_connection()
        thirty_days_later = datetime.date.today() + datetime.timedelta(days=30)
        count = conn.execute(
            "SELECT COUNT(*) FROM medicines WHERE expiry_date <= ?",
            (thirty_days_later,),
        ).fetchone()[0]
        conn.close()
        return count