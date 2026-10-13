import builtins
import os
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

original_import = builtins.__import__


def import_without_charts(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "PySide6.QtCharts":
        raise ImportError("simulated QtCharts DLL load failure")
    return original_import(name, globals, locals, fromlist, level)


with patch("builtins.__import__", side_effect=import_without_charts):
    import main

import database
from PySide6.QtWidgets import QApplication

assert main.CHARTS_AVAILABLE is False
db = database.Database(":memory:")
app = QApplication([])
with patch("main.Database", return_value=db):
    window = main.MainWindow()

try:
    assert window.statistics.employee_chart.objectName() == "chartFallback"
    assert window.statistics.daily_chart.objectName() == "chartFallback"
    assert "Эксел" in window.statistics.employee_chart.text()
finally:
    window.close()
    db.connection.close()

print("CHARTS_FALLBACK_OK")
