import sqlite3
import sys
from datetime import date
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
        CREATE TABLE IF NOT EXISTS work_types(id INTEGER PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,unit TEXT NOT NULL DEFAULT 'marta',note TEXT NOT NULL DEFAULT '',sort_order INTEGER NOT NULL DEFAULT 0,is_active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY,name TEXT NOT NULL COLLATE NOCASE UNIQUE,start_date TEXT NOT NULL,completed_at TEXT,note TEXT NOT NULL DEFAULT '',is_active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS project_employees(project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(project_id,employee_id));
        CREATE TABLE IF NOT EXISTS daily_entries(id INTEGER PRIMARY KEY,employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,work_type_id INTEGER NOT NULL REFERENCES work_types(id) ON DELETE RESTRICT,work_date TEXT NOT NULL,quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(employee_id,project_id,work_type_id,work_date));
        """)
        employee_columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(employees)")
        }
        if "department_id" not in employee_columns:
            self.connection.execute(
                "ALTER TABLE employees ADD COLUMN department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL"
            )
        work_type_columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(work_types)")
        }
        if "sort_order" not in work_type_columns:
            self.connection.execute(
                "ALTER TABLE work_types ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
            )
            self.connection.execute(
                "UPDATE work_types SET sort_order=id WHERE sort_order=0"
            )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_employees_department ON employees(department_id)"
        )
        self._migrate_daily_entries_projects()
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_entries_date ON daily_entries(work_date)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_project_employees_employee ON project_employees(employee_id)"
        )
        self.connection.commit()

    def _migrate_daily_entries_projects(self):
        columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(daily_entries)")
        }
        if "project_id" in columns:
            return

        legacy_count = self.connection.execute(
            "SELECT COUNT(*) FROM daily_entries"
        ).fetchone()[0]
        legacy_project_id = None
        if legacy_count:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO projects(name,start_date,completed_at,note,is_active)
                VALUES('Eski ma\u02bclumotlar','1900-01-01',date('now'),
                       'Loyiha tizimi qo\u02bbshilishidan oldingi hisobotlar',0)
                """
            )
            legacy_project_id = self.connection.execute(
                "SELECT id FROM projects WHERE name=?", ("Eski ma\u02bclumotlar",)
            ).fetchone()[0]

        self.connection.execute("ALTER TABLE daily_entries RENAME TO daily_entries_legacy")
        self.connection.execute(
            """
            CREATE TABLE daily_entries(
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
                work_type_id INTEGER NOT NULL REFERENCES work_types(id) ON DELETE RESTRICT,
                work_date TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id,project_id,work_type_id,work_date)
            )
            """
        )
        if legacy_project_id is not None:
            self.connection.execute(
                """
                INSERT INTO daily_entries(
                    id,employee_id,project_id,work_type_id,work_date,quantity,updated_at
                )
                SELECT id,employee_id,?,work_type_id,work_date,quantity,updated_at
                FROM daily_entries_legacy
                """,
                (legacy_project_id,),
            )
        self.connection.execute("DROP TABLE daily_entries_legacy")

    def all(self, table, include_inactive=True):
        where = "" if include_inactive else " WHERE is_active=1"
        if table == "employees":
            where = "" if include_inactive else " WHERE e.is_active=1"
            return self.connection.execute(
                f"""
                SELECT e.*, d.name AS department_name,
                       COALESCE((
                           SELECT GROUP_CONCAT(p.name, ', ')
                           FROM project_employees AS pe
                           JOIN projects AS p ON p.id=pe.project_id
                           WHERE pe.employee_id=e.id AND p.is_active=1
                       ), '') AS project_names
                FROM employees AS e
                LEFT JOIN departments AS d ON d.id = e.department_id
                {where}
                ORDER BY e.id DESC
                """
            ).fetchall()
        if table == "projects":
            return self.connection.execute(
                f"""
                SELECT p.*,
                       COALESCE((
                           SELECT GROUP_CONCAT(e.first_name || ' ' || e.last_name, ', ')
                           FROM project_employees AS pe
                           JOIN employees AS e ON e.id=pe.employee_id
                           WHERE pe.project_id=p.id
                       ), '') AS employee_names
                FROM projects AS p
                {where.replace('is_active', 'p.is_active')}
                ORDER BY p.is_active DESC, p.id DESC
                """
            ).fetchall()
        if table == "work_types":
            return self.connection.execute(
                f"SELECT * FROM work_types{where} ORDER BY sort_order, id"
            ).fetchall()
        return self.connection.execute(f"SELECT * FROM {table}{where} ORDER BY id DESC").fetchall()

    def add_employee(self, first, last, department_id=None, project_ids=None):
        cursor = self.connection.execute(
            "INSERT INTO employees(first_name,last_name,department_id) VALUES(?,?,?)",
            (first.strip(), last.strip(), department_id),
        )
        self.set_employee_projects(cursor.lastrowid, project_ids or [])
        self.connection.commit()

    def update_employee(self, row_id, first, last, department_id=None, project_ids=None):
        self.connection.execute(
            "UPDATE employees SET first_name=?,last_name=?,department_id=? WHERE id=?",
            (first.strip(), last.strip(), department_id, row_id),
        )
        if project_ids is not None:
            self.set_employee_projects(row_id, project_ids)
        self.connection.commit()

    def employee_project_ids(self, employee_id):
        return {
            row[0]
            for row in self.connection.execute(
                "SELECT project_id FROM project_employees WHERE employee_id=?",
                (employee_id,),
            )
        }

    def set_employee_projects(self, employee_id, project_ids):
        self.connection.execute(
            "DELETE FROM project_employees WHERE employee_id=?", (employee_id,)
        )
        self.connection.executemany(
            "INSERT INTO project_employees(project_id,employee_id) VALUES(?,?)",
            [(project_id, employee_id) for project_id in project_ids],
        )

    def add_project(self, name, start_date, note=""):
        self.connection.execute(
            "INSERT INTO projects(name,start_date,note) VALUES(?,?,?)",
            (name.strip(), start_date, note.strip()),
        )
        self.connection.commit()

    def update_project(self, row_id, name, start_date, note=""):
        self.connection.execute(
            "UPDATE projects SET name=?,start_date=?,note=? WHERE id=?",
            (name.strip(), start_date, note.strip(), row_id),
        )
        self.connection.commit()

    def complete_project(self, row_id, completed_at):
        self.connection.execute(
            "UPDATE projects SET is_active=0,completed_at=? WHERE id=?",
            (completed_at, row_id),
        )
        self.connection.commit()

    def reopen_project(self, row_id):
        self.connection.execute(
            "UPDATE projects SET is_active=1,completed_at=NULL WHERE id=?", (row_id,)
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
        next_order = self.connection.execute(
            "SELECT COALESCE(MAX(sort_order),0)+1 FROM work_types"
        ).fetchone()[0]
        self.connection.execute(
            "INSERT INTO work_types(name,sort_order) VALUES(?,?)",
            (name.strip(), next_order),
        )
        self.connection.commit()

    def update_work_type(self, row_id, name):
        self.connection.execute("UPDATE work_types SET name=? WHERE id=?", (name.strip(),row_id)); self.connection.commit()

    def move_work_type(self, row_id, direction, include_inactive=False):
        where = "" if include_inactive else " WHERE is_active=1"
        rows = self.connection.execute(
            f"SELECT id,sort_order FROM work_types{where} ORDER BY sort_order,id"
        ).fetchall()
        current_index = next(
            (index for index, row in enumerate(rows) if row["id"] == row_id), None
        )
        if current_index is None:
            return False
        target_index = current_index + direction
        if not 0 <= target_index < len(rows):
            return False
        current, target = rows[current_index], rows[target_index]
        self.connection.execute(
            "UPDATE work_types SET sort_order=? WHERE id=?",
            (target["sort_order"], current["id"]),
        )
        self.connection.execute(
            "UPDATE work_types SET sort_order=? WHERE id=?",
            (current["sort_order"], target["id"]),
        )
        self.connection.commit()
        return True

    def toggle_active(self, table, row_id, active):
        if table == "projects":
            if active:
                self.reopen_project(row_id)
            else:
                self.complete_project(row_id, date.today().isoformat())
            return
        self.connection.execute(f"UPDATE {table} SET is_active=? WHERE id=?", (int(active),row_id)); self.connection.commit()

    def delete_if_unused(self, table, row_id):
        if table == "departments":
            used = self.connection.execute(
                "SELECT EXISTS(SELECT 1 FROM employees WHERE department_id=?)", (row_id,)
            ).fetchone()[0]
        elif table == "projects":
            used = self.connection.execute(
                "SELECT EXISTS(SELECT 1 FROM daily_entries WHERE project_id=?)", (row_id,)
            ).fetchone()[0]
        else:
            key = "employee_id" if table == "employees" else "work_type_id"
            used = self.connection.execute(
                f"SELECT EXISTS(SELECT 1 FROM daily_entries WHERE {key}=?)", (row_id,)
            ).fetchone()[0]
        if used:
            if table == "projects":
                is_active = self.connection.execute(
                    "SELECT is_active FROM projects WHERE id=?", (row_id,)
                ).fetchone()[0]
                if is_active:
                    self.toggle_active(table, row_id, False)
            else:
                self.toggle_active(table, row_id, False)
            return False
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
        employee_ids = {employee["id"] for employee in employees}
        if employee_ids:
            placeholders = ",".join("?" for _ in employee_ids)
            assignments = self.connection.execute(
                f"""
                SELECT DISTINCT e.id AS employee_id,e.first_name,e.last_name,
                       p.id AS project_id,p.name AS project_name
                FROM employees AS e
                JOIN projects AS p
                  ON (
                      EXISTS(SELECT 1 FROM project_employees AS pe
                             WHERE pe.employee_id=e.id AND pe.project_id=p.id)
                      AND p.start_date<=?
                      AND (p.completed_at IS NULL OR p.completed_at>=?)
                  )
                  OR EXISTS(SELECT 1 FROM daily_entries AS de
                            WHERE de.employee_id=e.id AND de.project_id=p.id
                              AND de.work_date=?)
                WHERE e.id IN ({placeholders})
                ORDER BY e.last_name,e.first_name,p.name
                """,
                (work_date, work_date, work_date, *employee_ids),
            ).fetchall()
        else:
            assignments = []
        types = self.all("work_types",False)
        rows = self.connection.execute("SELECT employee_id,project_id,work_type_id,quantity FROM daily_entries WHERE work_date=?", (work_date,)).fetchall()
        values = {
            (row["employee_id"], row["project_id"], row["work_type_id"]): row["quantity"]
            for row in rows
            if row["employee_id"] in employee_ids
        }
        return assignments, types, values

    def save_quantity(self, employee_id, project_id, type_id, work_date, quantity):
        if quantity <= 0:
            self.connection.execute("DELETE FROM daily_entries WHERE employee_id=? AND project_id=? AND work_type_id=? AND work_date=?", (employee_id,project_id,type_id,work_date))
        else:
            self.connection.execute("""INSERT INTO daily_entries(employee_id,project_id,work_type_id,work_date,quantity) VALUES(?,?,?,?,?)
            ON CONFLICT(employee_id,project_id,work_type_id,work_date) DO UPDATE SET quantity=excluded.quantity,updated_at=CURRENT_TIMESTAMP""", (employee_id,project_id,type_id,work_date,quantity))
        self.connection.commit()

    def employee_totals(self, date_from, date_to, department_id=None, project_id=None):
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
              AND (? IS NULL OR d.project_id=?)
            GROUP BY e.id, e.first_name, e.last_name
            HAVING SUM(d.quantity) > 0
            ORDER BY total DESC, e.last_name, e.first_name
            """,
            (date_from, date_to, department_id, department_id, project_id, project_id),
        ).fetchall()

    def employee_daily_totals(self, employee_id, date_from, date_to, project_id=None):
        rows = self.connection.execute(
            """
            SELECT work_date, SUM(quantity) AS total
            FROM daily_entries
            WHERE employee_id=? AND work_date BETWEEN ? AND ?
              AND (? IS NULL OR project_id=?)
            GROUP BY work_date
            ORDER BY work_date
            """,
            (employee_id, date_from, date_to, project_id, project_id),
        ).fetchall()
        return {row["work_date"]: row["total"] for row in rows}

    def employee_daily_work_types(self, employee_id, date_from, date_to, project_id=None):
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
              AND (? IS NULL OR d.project_id=?)
            GROUP BY d.work_date, w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY w.name, d.work_date
            """,
            (employee_id, date_from, date_to, project_id, project_id),
        ).fetchall()

    def statistics_work_types(self, date_from, date_to, department_id=None, project_id=None):
        return self.connection.execute(
            """
            SELECT w.id, w.name, SUM(d.quantity) AS total
            FROM daily_entries AS d
            JOIN work_types AS w ON w.id = d.work_type_id
            JOIN employees AS e ON e.id = d.employee_id
            WHERE d.work_date BETWEEN ? AND ?
              AND (? IS NULL OR e.department_id=?)
              AND (? IS NULL OR d.project_id=?)
            GROUP BY w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY w.name
            """,
            (date_from, date_to, department_id, department_id, project_id, project_id),
        ).fetchall()

    def employee_work_type_totals(self, date_from, date_to, department_id=None, project_id=None):
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
              AND (? IS NULL OR d.project_id=?)
            GROUP BY e.id, e.first_name, e.last_name, e.department_id, w.id, w.name
            HAVING SUM(d.quantity) > 0
            ORDER BY e.last_name, e.first_name, w.name
            """,
            (date_from, date_to, department_id, department_id, project_id, project_id),
        ).fetchall()
