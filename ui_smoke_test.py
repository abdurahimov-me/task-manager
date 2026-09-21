import os
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import database
import main
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication


test_database = Path(__file__).resolve().parent / "data" / "ui_smoke_test.db"
test_database.unlink(missing_ok=True)
app = QApplication([])

with patch("main.Database", side_effect=lambda: database.Database(test_database)):
    window = main.MainWindow()
window.show()
app.processEvents()

db = window.db
try:
    db.add_department("Savdo")
    db.add_department("Moliya")
    department_ids = {
        row["name"]: row["id"] for row in db.all("departments", False)
    }
    db.add_employee("Ali", "Valiyev", department_ids["Savdo"])
    db.add_employee("Sami", "Karimov", department_ids["Moliya"])
    long_work_type = "Juda uzun nomli ish turi hisoboti"
    db.add_work_type(long_work_type)
    for index in range(7):
        db.add_work_type(f"Qo‘shimcha ish turi {index + 1}")

    employee_id = db.connection.execute(
        "SELECT id FROM employees WHERE first_name=?", ("Ali",)
    ).fetchone()[0]
    work_type_id = db.connection.execute(
        "SELECT id FROM work_types WHERE name=?", (long_work_type,)
    ).fetchone()[0]
    today = QDate.currentDate().toString("yyyy-MM-dd")
    db.save_quantity(employee_id, work_type_id, today, 4)
    for index in range(30):
        db.add_employee(f"Xodim {index + 1}", "Test", department_ids["Savdo"])
        extra_employee_id = db.connection.execute(
            "SELECT id FROM employees WHERE first_name=?", (f"Xodim {index + 1}",)
        ).fetchone()[0]
        db.save_quantity(extra_employee_id, work_type_id, today, 1)

    window.employees.load()
    app.processEvents()
    assert window.employees.table.horizontalHeaderItem(0).text() == "№"
    assert window.employees.table.item(0, 0).text() == "1"
    employee_widths = [
        window.employees.table.columnWidth(column) for column in range(5)
    ]
    assert employee_widths[0] == 56
    assert abs(sum(employee_widths) - window.employees.table.viewport().width()) <= 2
    assert abs(employee_widths[1] - employee_widths[2]) <= 2
    finance_filter = window.employees.department_filter.findData(
        department_ids["Moliya"]
    )
    window.employees.department_filter.setCurrentIndex(finance_filter)
    assert window.employees.table.rowCount() == 1
    assert window.employees.table.item(0, 1).text() == "Sami Karimov"
    assert window.employees.table.item(0, 0).text() == "1"

    window.departments.load()
    window.types.load()
    app.processEvents()
    assert window.departments.table.horizontalHeaderItem(0).text() == "№"
    assert window.types.table.horizontalHeaderItem(0).text() == "№"
    assert window.departments.table.columnWidth(0) == 56
    assert window.types.table.columnWidth(0) == 56
    assert abs(
        sum(window.departments.table.columnWidth(column) for column in range(3))
        - window.departments.table.viewport().width()
    ) <= 2
    assert abs(
        sum(window.types.table.columnWidth(column) for column in range(3))
        - window.types.table.viewport().width()
    ) <= 2

    window.daily.load()
    assert window.daily.department_tabs.count() == 2
    sales_tab = next(
        index
        for index in range(window.daily.department_tabs.count())
        if window.daily.department_tabs.tabData(index) == department_ids["Savdo"]
    )
    window.daily.department_tabs.setCurrentIndex(sales_tab)
    app.processEvents()
    assert window.daily.table.rowCount() == 31
    employee_names = [
        window.daily.employee_table.item(row, 0).text()
        for row in range(window.daily.employee_table.rowCount())
    ]
    assert "Valiyev Ali" in employee_names
    assert all(
        window.daily.table.columnWidth(column)
        == window.daily.WORK_TYPE_COLUMN_WIDTH
        for column in range(window.daily.table.columnCount())
    )
    assert window.daily.table.horizontalHeader().height() == window.daily.HEADER_HEIGHT
    long_work_type_column = next(
        column
        for column in range(window.daily.table.columnCount())
        if window.daily.table.horizontalHeaderItem(column).toolTip() == long_work_type
    )
    assert "\n" in window.daily.table.horizontalHeaderItem(long_work_type_column).text()
    assert window.daily.table.horizontalScrollBar().maximum() > 0
    assert window.daily.employee_table.objectName() == "frozenEmployees"
    window.daily.table.horizontalScrollBar().setValue(
        window.daily.table.horizontalScrollBar().maximum()
    )
    assert "Valiyev Ali" in [
        window.daily.employee_table.item(row, 0).text()
        for row in range(window.daily.employee_table.rowCount())
    ]

    window.toggle_sidebar()
    assert window.sidebar.width() == 76
    assert all(button.text() == icon for button, (icon, _) in zip(window.buttons, window.nav_items))
    window.toggle_sidebar()
    assert window.sidebar.width() == 238

    window.statistics.load()
    sales_filter = window.statistics.department_combo.findData(
        department_ids["Savdo"]
    )
    window.statistics.department_combo.setCurrentIndex(sales_filter)
    app.processEvents()
    assert window.statistics.total_metric.value.text() == "34"
    assert window.statistics.employee_metric.value.text() == "31"
    assert window.statistics.employee_chart.height() >= 85 + 31 * 36
    assert window.statistics.employee_chart_page.verticalScrollBar().maximum() > 0
    print("UI_SMOKE_OK")
finally:
    window.close()
    db.connection.close()
    test_database.unlink(missing_ok=True)
