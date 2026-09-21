import database
import sqlite3
from pathlib import Path

test_database = Path(__file__).resolve().parent / "data" / "smoke_test.db"
migration_database = Path(__file__).resolve().parent / "data" / "migration_test.db"
for path in (test_database, migration_database):
    path.unlink(missing_ok=True)
try:
    db = database.Database(test_database)
    db.add_department("__SMOKE_DEPARTMENT__")
    department_id = db.connection.execute(
        "SELECT id FROM departments WHERE name='__SMOKE_DEPARTMENT__'"
    ).fetchone()[0]
    db.add_department("__OTHER_DEPARTMENT__")
    other_department_id = db.connection.execute(
        "SELECT id FROM departments WHERE name='__OTHER_DEPARTMENT__'"
    ).fetchone()[0]
    db.add_employee("__SMOKE__", "__SMOKE__", department_id)
    db.add_employee("__OTHER__", "__OTHER__", other_department_id)
    db.add_work_type("__SMOKE_TYPE__")
    employee_id = db.connection.execute(
        "SELECT id FROM employees WHERE first_name='__SMOKE__'"
    ).fetchone()[0]
    work_type_id = db.connection.execute(
        "SELECT id FROM work_types WHERE name='__SMOKE_TYPE__'"
    ).fetchone()[0]
    other_employee_id = db.connection.execute(
        "SELECT id FROM employees WHERE first_name='__OTHER__'"
    ).fetchone()[0]
    db.save_quantity(employee_id, work_type_id, "2099-01-01", 3)
    db.save_quantity(other_employee_id, work_type_id, "2099-01-01", 7)
    assert db.daily_matrix("2099-01-01", department_id)[2] == {
        (employee_id, work_type_id): 3
    }
    assert db.daily_matrix("2099-01-01", 0)[0] == []
    totals = db.employee_totals("2099-01-01", "2099-01-31", department_id)
    assert [(row["id"], row["total"]) for row in totals] == [(employee_id, 3)]
    assert db.employee_daily_totals(employee_id, "2099-01-01", "2099-01-31") == {
        "2099-01-01": 3
    }
    work_type_totals = db.employee_daily_work_types(
        employee_id, "2099-01-01", "2099-01-31"
    )
    assert [
        (row["work_date"], row["work_type_id"], row["total"])
        for row in work_type_totals
    ] == [("2099-01-01", work_type_id, 3)]
    statistics_types = db.statistics_work_types(
        "2099-01-01", "2099-01-31", department_id
    )
    assert [(row["id"], row["total"]) for row in statistics_types] == [
        (work_type_id, 3)
    ]
    assert [
        (row["id"], row["total"])
        for row in db.statistics_work_types("2099-01-01", "2099-01-31")
    ] == [(work_type_id, 10)]
    employee_work = db.employee_work_type_totals(
        "2099-01-01", "2099-01-31", department_id
    )
    assert [
        (row["employee_id"], row["work_type_id"], row["total"])
        for row in employee_work
    ] == [(employee_id, work_type_id, 3)]
    assert db.delete_if_unused("departments", department_id) is False
    assert db.delete_if_unused("work_types", work_type_id) is False
    db.connection.close()

    legacy = sqlite3.connect(migration_database)
    legacy.execute(
        """
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    legacy.commit()
    legacy.close()
    migrated = database.Database(migration_database)
    migrated_columns = {
        row["name"]
        for row in migrated.connection.execute("PRAGMA table_info(employees)")
    }
    assert "department_id" in migrated_columns
    migrated.connection.close()
finally:
    for path in (test_database, migration_database):
        path.unlink(missing_ok=True)
print("DB_LOGIC_OK")
