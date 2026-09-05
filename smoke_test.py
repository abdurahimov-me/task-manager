import database

db = database.Database()
db.add_employee("__SMOKE__", "__SMOKE__")
db.add_work_type("__SMOKE_TYPE__")
employee_id = db.connection.execute("SELECT id FROM employees WHERE first_name='__SMOKE__'").fetchone()[0]
work_type_id = db.connection.execute("SELECT id FROM work_types WHERE name='__SMOKE_TYPE__'").fetchone()[0]
db.save_quantity(employee_id, work_type_id, "2099-01-01", 3)
assert db.daily_matrix("2099-01-01")[2][(employee_id, work_type_id)] == 3
totals = db.employee_totals("2099-01-01", "2099-01-31")
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
assert db.delete_if_unused("work_types", work_type_id) is False
assert db.connection.execute("SELECT is_active FROM work_types WHERE id=?", (work_type_id,)).fetchone()[0] == 0
db.connection.execute("DELETE FROM daily_entries WHERE employee_id=?", (employee_id,))
db.connection.execute("DELETE FROM employees WHERE id=?", (employee_id,))
db.connection.execute("DELETE FROM work_types WHERE id=?", (work_type_id,))
db.connection.commit()
print("DB_LOGIC_OK")
