import sqlite3
import sys
from pathlib import Path


def app_data_dir():
    base = Path.home() / "AppData" / "Local" / "HR Control" if getattr(sys, "frozen", False) else Path(__file__).resolve().parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else app_data_dir() / "hr_control.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,is_active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY,first_name TEXT NOT NULL,last_name TEXT NOT NULL,department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,phone TEXT NOT NULL DEFAULT '',note TEXT NOT NULL DEFAULT '',is_active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS work_types(id INTEGER PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,unit TEXT NOT NULL DEFAULT 'marta',note TEXT NOT NULL DEFAULT '',is_active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS daily_entries(id INTEGER PRIMARY KEY,employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,work_type_id INTEGER NOT NULL REFERENCES work_types(id) ON DELETE RESTRICT,work_date TEXT NOT NULL,quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(employee_id,work_type_id,work_date));
        CREATE INDEX IF NOT EXISTS ix_entries_date ON daily_entries(work_date);
        """)
        employee_columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(employees)")
        }
        if "department_id" not in employee_columns:
            self.connection.execute(
                "ALTER TABLE employees ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL"
            )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_employees_department ON employees(department_id)"
        )
        self.connection.commit()

    def all(self, table, include_inactive=True):
        where = "" if include_inactive else " WHERE is_active=1"
        if table == "employees":
            where = "" if include_inactive else " WHERE e.is_active=1"
            return self.connection.execute(
                f"""
                SELECT e.*, d.name AS department_name
                FROM employees AS e
                LEFT JOIN departments AS d ON d.id = e.department_id
                {where}
                ORDER BY e.id DESC
                """
            ).fetchall()
        return self.connection.execute(f"SELECT * FROM {table}{where} ORDER BY id DESC").fetchall()

    def add_employee(self, first, last, department_id=None):
        self.connection.execute(
            "INSERT INTO employees(first_name,last_name,department_id) VALUES(?,?,?)",
            (first.strip(), last.strip(), department_id),
        )
        self.connection.commit()

    def update_employee(self, row_id, first, last, department_id=None):
        self.connection.execute(
            "UPDATE employees SET first_name=?,last_name=?,department_id=? WHERE id=?",
            (first.strip(), last.strip(), department_id, row_id),
        )
        self.connection.commit()

    def add_department(self, name):
        self.connection.execute(
            "INSERT INTO departments(name) VALUES(?)", (name.strip(),)
        )
        self.connection.commit()

    def update_department(self, row_id, name):
        self.connection.execute(
            "UPDATE departments SET name=? WHERE id=?", (name.strip(), row_id)
        )
        self.connection.commit()

    def add_work_type(self, name):
        self.connection.execute("INSERT INTO work_types(name) VALUES(?)", (name.strip(),)); self.connection.commit()

    def update_work_type(self, row_id, name):
        self.connection.execute("UPDATE work_types SET name=? WHERE id=?", (name.strip(),row_id)); self.connection.commit()

    def toggle_active(self, table, row_id, active):
        self.connection.execute(f"UPDATE {table} SET is_active=? WHERE id=?", (int(active),row_id)); self.connection.commit()

    def delete_if_unused(self, table, row_id):
        if table == "departments":
            used = self.connection.execute(
                "SELECT EXISTS(SELECT 1 FROM employees WHERE department_id=?)", (row_id,)
            ).fetchone()[0]
        else:
            key = "employee_id" if table == "employees" else "work_type_id"
            used = self.connection.execute(
                f"SELECT EXISTS(SELECT 1 FROM daily_entries WHERE {key}=?)", (row_id,)
            ).fetchone()[0]
        if used:
            self.toggle_active(table,row_id,False); return False
        self.connection.execute(f"DELETE FROM {table} WHERE id=?", (row_id,)); self.connection.commit(); return True

    def daily_departments(self):
        departments = self.connection.execute(
            """
            SELECT d.*
            FROM departments AS d
            WHERE d.is_active=1
               OR EXISTS(
                    SELECT 1 FROM employees AS e
                    WHERE e.department_id=d.id AND e.is_active=1
               )
            ORDER BY d.name
            """
        ).fetchall()
        has_unassigned = bool(
            self.connection.execute(
                "SELECT EXISTS(SELECT 1 FROM employees WHERE is_active=1 AND department_id IS NULL)"
            ).fetchone()[0]
        )
        return departments, has_unassigned

    def daily_matrix(self, work_date, department_id=None):
        if department_id == 0:
            employees = self.connection.execute(
                """
                SELECT e.*, NULL AS department_name
                FROM employees AS e
                WHERE e.is_active=1 AND e.department_id IS NULL
                ORDER BY e.id DESC
                """
            ).fetchall()
        elif department_id is None:
            employees = []
        else:
            employees = self.connection.execute(
                """
                SELECT e.*, d.name AS department_name
                FROM employees AS e
                LEFT JOIN departments AS d ON d.id=e.department_id
                WHERE e.is_active=1 AND e.department_id=?
                ORDER BY e.id DESC
                """,
                (department_id,),
            ).fetchall()
        types = self.all("work_types",False)
        rows = self.connection.execute("SELECT employee_id,work_type_id,quantity FROM daily_entries WHERE work_date=?", (work_date,)).fetchall()
        employee_ids = {employee["id"] for employee in employees}
        values = {
            (row["employee_id"], row["work_type_id"]): row["quantity"]
            for row in rows
            if row["employee_id"] in employee_ids
        }
        return employees, types, values

    def save_quantity(self, employee_id, type_id, work_date, quantity):
        if quantity <= 0:
            self.connection.execute("DELETE FROM daily_entries WHERE employee_id=? AND work_type_id=? AND work_date=?", (employee_id,type_id,work_date))
        else:
            self.connection.execute("""INSERT INTO daily_entries(employee_id,work_type_id,work_date,quantity) VALUES(?,?,?,?)
            ON CONFLICT(employee_id,work_type_id,work_date) DO UPDATE SET quantity=excluded.quantity,updated_at=CURRENT_TIMESTAMP""", (employee_id,type_id,work_date,quantity))
        self.connection.commit()

    def employee_totals(self, date_from, date_to, department_id=None):
        return self.connection.execute(
            """
            SELECT
                e.id,
                e.first_name,
                e.last_name,
                SUM(d.quantity) AS total
            FROM daily_entries AS d 
            JOIN employees AS e ON e.id = d.employee_id
            WHERE d.work_date BETWEEN ? AND ?
              AND (? IS NULL OR e.department_id=?)
            GROUP BY e.id, e.first_name, e.last_name
            HAVING SUM(d.quantity) > 0
            ORDER BY total DESC, e.last_name, e.first_name
            """,
            (date_from, date_to, department_id, department_id),
        ).fetchall()

    def employee_daily_totals(self, employee_id, date_from, date_to):
        rows = self.connection.execute(
            """
            SELECT work_date, SUM(quantity) AS total
            FROM daily_entries
            WHERE employee_id=? AND work_date BETWEEN ? AND ?
            GROUP BY work_date
            ORDER BY work_date
            """,
            (employee_id, date_from, date_to),
        ).fetchall()
        return {row["work_date"]: row["total"] for row in rows}

    def employee_daily_work_types(self, employee_id, date_from, date_to):
        return self.connection.execute(
            """
            SELECT
                d.work_date,
                w.id AS work_type_id,
                w.name AS work_type_name,
                SUM(d.quantity) AS total
            FROM daily_entries AS d
            JOIN work_types AS w ON w.id = d.work_type_id
            WHERE d.employee_id=? AND d.work_date BETWEEN ? AND ?
            GROUP BY d.work_date, w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY w.name, d.work_date
            """,
            (employee_id, date_from, date_to),
        ).fetchall()

    def statistics_work_types(self, date_from, date_to, department_id=None):
        return self.connection.execute(
            """
            SELECT w.id, w.name, SUM(d.quantity) AS total
            FROM daily_entries AS d
            JOIN work_types AS w ON w.id = d.work_type_id
            JOIN employees AS e ON e.id = d.employee_id
            WHERE d.work_date BETWEEN ? AND ?
              AND (? IS NULL OR e.department_id=?)
            GROUP BY w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY w.name
            """,
            (date_from, date_to, department_id, department_id),
        ).fetchall()

    def employee_work_type_totals(self, date_from, date_to, department_id=None):
        return self.connection.execute(
            """
            SELECT
                e.id AS employee_id,
                e.first_name,
                e.last_name,
                e.department_id,
                w.id AS work_type_id,
                w.name AS work_type_name,
                SUM(d.quantity) AS total
            FROM daily_entries AS d
            JOIN employees AS e ON e.id = d.employee_id
            JOIN work_types AS w ON w.id = d.work_type_id
            WHERE d.work_date BETWEEN ? AND ?
              AND (? IS NULL OR e.department_id=?)
            GROUP BY e.id, e.first_name, e.last_name, e.department_id, w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY e.last_name, e.first_name, w.name
            """,
            (date_from, date_to, department_id, department_id),
        ).fetchall()
