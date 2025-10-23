import reflex as rx
from typing import TypedDict, Literal
import datetime
import logging
from .db_state import get_db_connection
import csv
import io

ReportType = Literal[
    "sales", "stock", "expiry", "low_stock", "supplier_purchases", "customer_purchases"
]


class ReportRow(TypedDict):
    pass


class ReportsState(rx.State):
    active_report: ReportType = "sales"
    report_data: list[ReportRow] = []
    start_date: str = (datetime.date.today() - datetime.timedelta(days=30)).strftime(
        "%Y-%m-%d"
    )
    end_date: str = datetime.date.today().strftime("%Y-%m-%d")
    loading: bool = False

    @rx.event
    def set_active_report(self, report_type: ReportType):
        self.active_report = report_type
        return ReportsState.fetch_report_data

    @rx.event
    def fetch_report_data(self):
        self.loading = True
        self.report_data = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.active_report == "sales":
                cursor.execute(
                    "SELECT strftime('%Y-%m-%d', sale_date) as date, SUM(total_amount) as total FROM sales WHERE date(sale_date) BETWEEN ? AND ? GROUP BY date ORDER BY date DESC",
                    (self.start_date, self.end_date),
                )
            elif self.active_report == "stock":
                cursor.execute(
                    "SELECT name, batch_no, quantity, purchase_price, sale_price FROM medicines ORDER BY name"
                )
            elif self.active_report == "expiry":
                cursor.execute(
                    "SELECT name, batch_no, expiry_date, quantity FROM medicines WHERE date(expiry_date) BETWEEN ? AND ? ORDER BY expiry_date ASC",
                    (self.start_date, self.end_date),
                )
            elif self.active_report == "low_stock":
                cursor.execute(
                    "SELECT name, batch_no, quantity FROM medicines WHERE quantity < 10 ORDER BY quantity ASC"
                )
            elif self.active_report == "supplier_purchases":
                cursor.execute(
                    """
                    SELECT s.name as supplier_name, m.name as medicine_name, p.quantity, p.purchase_date 
                    FROM purchases p
                    JOIN suppliers s ON p.supplier_id = s.id
                    JOIN medicines m ON p.medicine_id = m.id
                    WHERE date(p.purchase_date) BETWEEN ? AND ?
                    ORDER BY s.name, p.purchase_date DESC
                """,
                    (self.start_date, self.end_date),
                )
            elif self.active_report == "customer_purchases":
                cursor.execute(
                    """
                    SELECT c.name as customer_name, strftime('%Y-%m-%d', s.sale_date) as date, s.total_amount
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id
                    WHERE date(s.sale_date) BETWEEN ? AND ?
                    ORDER BY c.name, date DESC
                """,
                    (self.start_date, self.end_date),
                )
            self.report_data = [dict(row) for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logging.exception(f"Error fetching report: {e}")
            yield rx.toast.error(f"Failed to fetch report data: {e}")
        finally:
            self.loading = False

    @rx.event
    def download_csv(self):
        if not self.report_data:
            return rx.toast.warning("No data to download.")
        output = io.StringIO()
        writer = csv.writer(output)
        headers = self.report_data[0].keys()
        writer.writerow(headers)
        for row in self.report_data:
            writer.writerow(row.values())
        csv_data = output.getvalue()
        output.close()
        filename = f"{self.active_report}_report_{datetime.date.today()}.csv"
        return rx.download(data=csv_data, filename=filename)