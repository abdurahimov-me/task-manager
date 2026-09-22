import sqlite3
import sys
from pathlib import Path
from textwrap import wrap

from PySide6.QtCharts import (
    QAbstractBarSeries,
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QChartView,
    QDateTimeAxis,
    QHorizontalBarSeries,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import QDate, QDateTime, QEvent, QLocale, QMargins, QTime, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QAbstractSpinBox,
    QAbstractItemView,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTabBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import Database


STYLE = """
* {
    font-family: 'Segoe UI';
    font-size: 13px;
    color: #344054;
}
QMainWindow, QWidget#root, QWidget#page {
    background: #f6f7fb;
}
QFrame#sidebar {
    background: #101828;
    border: 0;
}
QFrame#logoMark {
    background: #2f6fed;
    border: 0;
    border-radius: 11px;
}
QLabel#logoText {
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
}
QLabel#brand {
    color: #ffffff;
    font-size: 17px;
    font-weight: 700;
}
QLabel#brandSub, QLabel#navSection {
    color: #667085;
    font-size: 10px;
    font-weight: 700;
}
QPushButton#nav {
    background: transparent;
    color: #98a2b3;
    text-align: left;
    border: 0;
    border-radius: 9px;
    padding: 11px 14px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#nav:hover {
    background: #1d2939;
    color: #eaecf0;
}
QPushButton#nav[active="true"] {
    background: #243b64;
    color: #ffffff;
    font-weight: 650;
}
QPushButton#nav[collapsed="true"] {
    text-align: center;
    padding: 10px 0;
    font-size: 19px;
}
QPushButton#sidebarToggle {
    background: #1d2939;
    color: #98a2b3;
    border: 0;
    border-radius: 8px;
    padding: 0;
    font-size: 20px;
    font-weight: 700;
}
QPushButton#sidebarToggle:hover {
    background: #243b64;
    color: #ffffff;
}
QFrame#sidebarLine {
    background: #1d2939;
    border: 0;
    min-height: 1px;
    max-height: 1px;
}
QLabel#sidebarFoot {
    color: #667085;
    font-size: 11px;
}
QLabel#title {
    color: #101828;
    font-size: 26px;
    font-weight: 700;
}
QLabel#subtitle, QLabel#muted {
    color: #667085;
}
QLabel#sectionTitle {
    color: #1d2939;
    font-size: 15px;
    font-weight: 650;
}
QLabel#sectionMeta {
    color: #98a2b3;
    font-size: 12px;
}
QLabel#selectionChip {
    background: #eef4ff;
    color: #2f6fed;
    border: 1px solid #dbe5ff;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#emptyMark {
    background: #eef4ff;
    color: #2f6fed;
    border-radius: 22px;
    font-size: 20px;
    font-weight: 700;
}
QLabel#emptyTitle {
    color: #1d2939;
    font-size: 16px;
    font-weight: 650;
}
QLabel#emptyText {
    color: #98a2b3;
    font-size: 12px;
}
QFrame#surface, QFrame#metric {
    background: #ffffff;
    border: 1px solid #e4e7ec;
    border-radius: 12px;
}
QFrame#metric[accent="true"] {
    background: #f4f7ff;
    border: 1px solid #dbe5ff;
}
QLabel#metricLabel {
    color: #667085;
    font-size: 12px;
    font-weight: 500;
}
QLabel#metricValue {
    color: #101828;
    font-size: 23px;
    font-weight: 700;
}
QLabel#metricValue[accent="true"] {
    color: #2f6fed;
}
QLineEdit, QDateEdit, QComboBox {
    background: #ffffff;
    color: #1d2939;
    border: 1px solid #d0d5dd;
    border-radius: 8px;
    padding: 8px 11px;
    selection-background-color: #dbe7ff;
    min-height: 22px;
}
QLineEdit:hover, QDateEdit:hover, QComboBox:hover {
    border-color: #98a2b3;
}
QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid #2f6fed;
}
QDateEdit::drop-down {
    width: 24px;
    border: 0;
}
QPushButton#datePickerButton {
    background: transparent;
    color: #667085;
    border: 0;
    border-left: 1px solid #eaecf0;
    border-radius: 0;
    padding: 0;
    font-size: 14px;
}
QPushButton#datePickerButton:hover {
    background: #f2f4f7;
    color: #2f6fed;
}
QComboBox::drop-down {
    width: 28px;
    border: 0;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #344054;
    border: 1px solid #d0d5dd;
    border-radius: 7px;
    padding: 4px;
    selection-background-color: #eef4ff;
    selection-color: #1d2939;
    outline: 0;
}
QCheckBox {
    color: #475467;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background: #ffffff;
    border: 1px solid #d0d5dd;
    border-radius: 4px;
}
QCheckBox::indicator:hover {
    border-color: #2f6fed;
}
QCheckBox::indicator:checked {
    background: #2f6fed;
    border-color: #2f6fed;
}
QPushButton {
    border: 0;
    border-radius: 8px;
    padding: 9px 15px;
    min-height: 20px;
    font-weight: 600;
}
QPushButton#primary {
    background: #2f6fed;
    color: #ffffff;
}
QPushButton#primary:hover {
    background: #255dcc;
}
QPushButton#primary:pressed {
    background: #1f4fab;
}
QPushButton#secondary {
    background: #ffffff;
    color: #344054;
    border: 1px solid #d0d5dd;
}
QPushButton#secondary:hover {
    background: #f9fafb;
    border-color: #98a2b3;
}
QPushButton#quiet {
    background: #f2f4f7;
    color: #475467;
}
QPushButton#quiet:hover {
    background: #e4e7ec;
}
QPushButton#danger {
    background: #ffffff;
    color: #d92d20;
    border: 1px solid #fecdca;
}
QPushButton#danger:hover {
    background: #fef3f2;
}
QPushButton#dateNav {
    background: #ffffff;
    color: #475467;
    border: 1px solid #d0d5dd;
    min-width: 18px;
    padding: 8px 10px;
}
QPushButton#dateNav:hover {
    background: #f9fafb;
    border-color: #98a2b3;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #fcfcfd;
    border: 0;
    outline: 0;
    gridline-color: #eaecf0;
    selection-background-color: #eef4ff;
    selection-color: #1d2939;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f2f4f7;
}
QTableWidget::item:selected {
    background: #eef4ff;
    color: #1d2939;
}
QTableWidget#frozenEmployees {
    background: #f8fafc;
    alternate-background-color: #f4f7fb;
    border: 0;
    border-right: 2px solid #98a2b3;
}
QTableWidget#frozenEmployees::item {
    background: #f8fafc;
    color: #1d2939;
    font-weight: 600;
}
QTableWidget#frozenEmployees QHeaderView::section {
    background: #eef4ff;
    color: #2459c4;
    border-right: 2px solid #98a2b3;
}
QHeaderView {
    background: #f9fafb;
}
QHeaderView::section {
    background: #f9fafb;
    color: #667085;
    border: 0;
    border-bottom: 1px solid #eaecf0;
    padding: 11px 12px;
    font-size: 11px;
    font-weight: 700;
}
QTabBar#departmentTabs {
    background: #ffffff;
    border-bottom: 1px solid #eaecf0;
}
QTabBar#departmentTabs::tab {
    background: #ffffff;
    color: #667085;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 11px 18px;
    min-width: 90px;
    font-weight: 600;
}
QTabBar#departmentTabs::tab:hover {
    color: #2f6fed;
    background: #f9fafb;
}
QTabBar#departmentTabs::tab:selected {
    color: #2f6fed;
    border-bottom-color: #2f6fed;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #d0d5dd;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #f2f4f7;
    height: 9px;
    margin: 1px 3px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #b9c2d0;
    min-width: 38px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #98a2b3;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QDialog {
    background: #ffffff;
}
QLabel#dialogTitle {
    color: #101828;
    font-size: 20px;
    font-weight: 700;
}
QLabel#fieldLabel {
    color: #344054;
    font-size: 12px;
    font-weight: 600;
}
QFrame#dialogLine {
    background: #eaecf0;
    border: 0;
    min-height: 1px;
    max-height: 1px;
}
QMessageBox {
    background: #ffffff;
}
QToolTip, QLabel#chartTooltip {
    background: #101828;
    color: #ffffff;
    border: 0;
    padding: 6px;
}
"""

UZ_MONTHS = (
    "yanvar",
    "fevral",
    "mart",
    "aprel",
    "may",
    "iyun",
    "iyul",
    "avgust",
    "sentabr",
    "oktabr",
    "noyabr",
    "dekabr",
)


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path


def button(text, object_name, callback=None):
    control = QPushButton(text)
    control.setObjectName(object_name)
    control.setCursor(Qt.PointingHandCursor)
    if callback:
        control.clicked.connect(callback)
    return control


def configure_table(table):
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(47)
    table.horizontalHeader().setHighlightSections(False)


class QuantityTable(QTableWidget):
    MAX_QUANTITY = 999_999_999

    def __init__(self):
        super().__init__()
        self.typing_cell = None
        self.typing_buffer = ""
        self.typing_timer = QTimer(self)
        self.typing_timer.setSingleShot(True)
        self.typing_timer.setInterval(1200)
        self.typing_timer.timeout.connect(self.reset_typing)

    def reset_typing(self):
        self.typing_cell = None
        self.typing_buffer = ""

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ShiftModifier:
            scrollbar = self.horizontalScrollBar()
            pixel_delta = event.pixelDelta()
            if not pixel_delta.isNull():
                distance = pixel_delta.y() or pixel_delta.x()
            else:
                angle_delta = event.angleDelta()
                distance = round(
                    (angle_delta.y() or angle_delta.x())
                    / 120
                    * QApplication.wheelScrollLines()
                    * scrollbar.singleStep()
                )
            scrollbar.setValue(scrollbar.value() - distance)
            event.accept()
            return
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        row, column = self.currentRow(), self.currentColumn()
        if row >= 0 and column >= 0:
            cell = (row, column)
            text = event.text()

            if len(text) == 1 and text in "0123456789":
                if self.typing_cell != cell or not self.typing_timer.isActive():
                    self.typing_buffer = ""
                candidate = (self.typing_buffer + text).lstrip("0") or "0"
                value = min(int(candidate), self.MAX_QUANTITY)
                self.typing_buffer = str(value)
                self.typing_cell = cell
                self.item(row, column).setText(self.typing_buffer)
                self.typing_timer.start()
                event.accept()
                return

            if event.key() == Qt.Key_Backspace:
                if self.typing_cell != cell or not self.typing_timer.isActive():
                    self.typing_buffer = self.item(row, column).text()
                self.typing_buffer = self.typing_buffer[:-1] or "0"
                self.typing_cell = cell
                self.item(row, column).setText(self.typing_buffer)
                self.typing_timer.start()
                event.accept()
                return

            if event.key() == Qt.Key_Delete:
                self.item(row, column).setText("0")
                self.reset_typing()
                event.accept()
                return

        self.reset_typing()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.reset_typing()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        self.reset_typing()
        super().focusOutEvent(event)


class CalendarDateEdit(QDateEdit):
    """Date field with stable manual editing and an optional calendar popup."""

    def __init__(self, selected_date):
        super().__init__(selected_date)
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setDisplayFormat("dd.MM.yyyy")
        self.setKeyboardTracking(False)
        self.setMinimumWidth(145)
        self.setToolTip("Sanani yozing yoki o‘ngdagi tugmadan kalendarni oching")
        self.lineEdit().setReadOnly(False)
        self.lineEdit().setCursor(Qt.IBeamCursor)
        self.lineEdit().setTextMargins(0, 0, 30, 0)

        self.calendar_button = QPushButton("▾", self)
        self.calendar_button.setObjectName("datePickerButton")
        self.calendar_button.setCursor(Qt.PointingHandCursor)
        self.calendar_button.setToolTip("Kalendarni ochish")
        self.calendar_button.clicked.connect(self.show_calendar)

        self.popup_calendar = QCalendarWidget()
        self.popup_calendar.setWindowFlags(Qt.Popup)
        self.popup_calendar.setGridVisible(False)
        self.popup_calendar.clicked.connect(self.choose_date)
        self.dateChanged.connect(self.popup_calendar.setSelectedDate)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.calendar_button.setGeometry(self.width() - 35, 1, 34, self.height() - 2)

    def show_calendar(self):
        self.popup_calendar.setSelectedDate(self.date())
        self.popup_calendar.adjustSize()
        position = self.mapToGlobal(self.rect().bottomLeft())
        screen = QApplication.screenAt(position) or self.screen()
        bounds = screen.availableGeometry()
        x = min(position.x(), bounds.right() - self.popup_calendar.width() + 1)
        y = position.y() + 4
        if y + self.popup_calendar.height() > bounds.bottom() + 1:
            y = self.mapToGlobal(self.rect().topLeft()).y() - self.popup_calendar.height() - 4
        self.popup_calendar.move(max(bounds.left(), x), max(bounds.top(), y))
        self.popup_calendar.show()
        self.popup_calendar.raise_()

    def choose_date(self, selected_date):
        self.setDate(selected_date)
        self.popup_calendar.hide()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Space, Qt.Key_Down) and event.modifiers() & Qt.AltModifier:
            self.show_calendar()
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        event.ignore()


class MetricCard(QFrame):
    def __init__(self, label, value="0", accent=False):
        super().__init__()
        self.setObjectName("metric")
        self.setProperty("accent", accent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(3)

        caption = QLabel(label)
        caption.setObjectName("metricLabel")
        self.value = QLabel(value)
        self.value.setObjectName("metricValue")
        self.value.setProperty("accent", accent)
        layout.addWidget(caption)
        layout.addWidget(self.value)

    def set_value(self, value):
        self.value.setText(str(value))


class EmptyState(QWidget):
    def __init__(self, title, description):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 60)
        layout.setSpacing(7)
        layout.setAlignment(Qt.AlignCenter)

        mark = QLabel("+")
        mark.setObjectName("emptyMark")
        mark.setFixedSize(44, 44)
        mark.setAlignment(Qt.AlignCenter)
        heading = QLabel(title)
        heading.setObjectName("emptyTitle")
        heading.setAlignment(Qt.AlignCenter)
        text = QLabel(description)
        text.setObjectName("emptyText")
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        layout.addWidget(mark, 0, Qt.AlignCenter)
        layout.addWidget(heading)
        layout.addWidget(text)


class EntityDialog(QDialog):
    def __init__(self, kind, row=None, parent=None, db=None):
        super().__init__(parent)
        self.kind = kind
        self.db = db
        nouns = {
            "employees": "Xodim",
            "work_types": "Ish turi",
            "departments": "Bo‘lim",
            "projects": "Loyiha",
        }
        noun = nouns[kind]
        action = "Tahrirlash" if row else "Yangi qo‘shish"
        self.setWindowTitle(f"{noun} — {action}")
        self.setModal(True)
        self.setMinimumWidth(430)

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(18)

        title = QLabel(f"{noun}ni tahrirlash" if row else f"Yangi {noun.lower()}")
        title.setObjectName("dialogTitle")
        description = QLabel("Ma’lumotlarni kiriting va saqlash tugmasini bosing.")
        description.setObjectName("muted")
        root.addWidget(title)
        root.addWidget(description)

        if kind == "employees":
            self.first = self.add_field(root, "Ism *", row["first_name"] if row else "")
            self.last = self.add_field(root, "Familiya *", row["last_name"] if row else "")
            department_label = QLabel("Bo‘lim *")
            department_label.setObjectName("fieldLabel")
            self.department = QComboBox()
            self.department.addItem("Bo‘limni tanlang", None)
            departments = list(db.all("departments", False)) if db else []
            current_department_id = row["department_id"] if row else None
            if current_department_id and not any(
                department["id"] == current_department_id for department in departments
            ):
                departments.extend(
                    department
                    for department in db.all("departments", True)
                    if department["id"] == current_department_id
                )
            for department in departments:
                suffix = " (arxivda)" if not department["is_active"] else ""
                self.department.addItem(
                    f'{department["name"]}{suffix}', department["id"]
                )
            selected_index = self.department.findData(current_department_id)
            self.department.setCurrentIndex(max(0, selected_index))
            root.addWidget(department_label)
            root.addWidget(self.department)
            projects_label = QLabel("Biriktirilgan loyihalar")
            projects_label.setObjectName("fieldLabel")
            root.addWidget(projects_label)
            selected_project_ids = db.employee_project_ids(row["id"]) if row else set()
            projects = [
                project
                for project in db.all("projects", True)
                if project["is_active"] or project["id"] in selected_project_ids
            ]
            self.project_checks = []
            project_scroll = QScrollArea()
            project_scroll.setWidgetResizable(True)
            project_scroll.setFrameShape(QFrame.NoFrame)
            project_scroll.setMinimumHeight(90)
            project_scroll.setMaximumHeight(150)
            project_box = QWidget()
            project_layout = QVBoxLayout(project_box)
            project_layout.setContentsMargins(10, 8, 10, 8)
            project_layout.setSpacing(8)
            if projects:
                for project in projects:
                    suffix = " (yakunlangan)" if not project["is_active"] else ""
                    check = QCheckBox(f'{project["name"]}{suffix}')
                    check.setProperty("project_id", project["id"])
                    check.setChecked(project["id"] in selected_project_ids)
                    check.setEnabled(bool(project["is_active"]))
                    self.project_checks.append(check)
                    project_layout.addWidget(check)
            else:
                no_projects = QLabel("Faol loyihalar hali yo‘q")
                no_projects.setObjectName("muted")
                project_layout.addWidget(no_projects)
            project_layout.addStretch()
            project_scroll.setWidget(project_box)
            project_scroll.setStyleSheet(
                "QScrollArea { background:#f9fafb; border:1px solid #eaecf0; border-radius:8px; }"
            )
            root.addWidget(project_scroll)
        elif kind == "projects":
            self.name = self.add_field(root, "Loyiha nomi *", row["name"] if row else "")
            start_label = QLabel("Boshlanish sanasi *")
            start_label.setObjectName("fieldLabel")
            start_date = QDate.fromString(row["start_date"], Qt.ISODate) if row else QDate.currentDate()
            self.start_date = CalendarDateEdit(start_date)
            root.addWidget(start_label)
            root.addWidget(self.start_date)
            self.note = self.add_field(root, "Izoh", row["note"] if row else "")
        else:
            field_label = "Ish turi nomi *" if kind == "work_types" else "Bo‘lim nomi *"
            self.name = self.add_field(root, field_label, row["name"] if row else "")

        line = QFrame()
        line.setObjectName("dialogLine")
        root.addWidget(line)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()
        actions.addWidget(button("Bekor qilish", "secondary", self.reject))
        actions.addWidget(button("Saqlash", "primary", self.validate))
        root.addLayout(actions)

    @staticmethod
    def add_field(layout, label, value):
        caption = QLabel(label)
        caption.setObjectName("fieldLabel")
        field = QLineEdit(value)
        field.setClearButtonEnabled(True)
        layout.addWidget(caption)
        layout.addWidget(field)
        return field

    def validate(self):
        if self.kind == "employees":
            valid = (
                self.first.text().strip()
                and self.last.text().strip()
                and self.department.currentData() is not None
            )
        else:
            valid = self.name.text().strip()
        if valid:
            self.accept()
            return
        QMessageBox.warning(self, "Majburiy maydon", "Majburiy maydonlarni to‘ldiring.")

    def values(self):
        if self.kind == "employees":
            return (
                self.first.text().strip(),
                self.last.text().strip(),
                self.department.currentData(),
                [
                    check.property("project_id")
                    for check in self.project_checks
                    if check.isChecked()
                ],
            )
        if self.kind == "projects":
            return (
                self.name.text().strip(),
                self.start_date.date().toString("yyyy-MM-dd"),
                self.note.text().strip(),
            )
        return (self.name.text().strip(),)


class ProjectCompletionDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loyihani yakunlash")
        self.setModal(True)
        self.setMinimumWidth(420)
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(15)

        title = QLabel("Loyihani yakunlash")
        title.setObjectName("dialogTitle")
        description = QLabel(
            f'“{project["name"]}” yakunlangach, yangi kunlik hisobda ko‘rinmaydi. '
            "Oldingi hisobotlar va statistika saqlanib qoladi."
        )
        description.setObjectName("muted")
        description.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(description)

        label = QLabel("Tugash sanasi *")
        label.setObjectName("fieldLabel")
        start_date = QDate.fromString(project["start_date"], Qt.ISODate)
        selected_date = max(start_date, QDate.currentDate())
        self.completed_at = CalendarDateEdit(selected_date)
        self.completed_at.setMinimumDate(start_date)
        root.addWidget(label)
        root.addWidget(self.completed_at)

        line = QFrame()
        line.setObjectName("dialogLine")
        root.addWidget(line)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(button("Bekor qilish", "secondary", self.reject))
        actions.addWidget(button("Loyihani yakunlash", "primary", self.accept))
        root.addLayout(actions)

    def value(self):
        return self.completed_at.date().toString("yyyy-MM-dd")


class CrudPage(QWidget):
    changed = Signal()
    INDEX_COLUMN_WIDTH = 56

    def __init__(self, db, kind):
        super().__init__()
        self.setObjectName("page")
        self.db = db
        self.kind = kind
        self.rows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 27, 34, 30)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        headings = QVBoxLayout()
        headings.setSpacing(4)
        titles = {
            "employees": "Xodimlar",
            "work_types": "Ish turlari",
            "departments": "Bo‘limlar",
            "projects": "Loyihalar",
        }
        title = QLabel(titles[kind])
        title.setObjectName("title")
        subtitles = {
            "employees": "Jamoa a’zolari, ularning bo‘limi va holatini boshqaring",
            "work_types": "Kunlik hisobda ishlatiladigan ish turlarini boshqaring",
            "departments": "Xodimlarni ajratish uchun tashkilot bo‘limlarini boshqaring",
            "projects": "Loyihalarni, ularning muddatlari va holatini boshqaring",
        }
        subtitle = QLabel(subtitles[kind])
        subtitle.setObjectName("subtitle")
        headings.addWidget(title)
        headings.addWidget(subtitle)
        header.addLayout(headings)
        header.addStretch()
        add_texts = {
            "employees": "+  Xodim qo‘shish",
            "work_types": "+  Ish turi qo‘shish",
            "departments": "+  Bo‘lim qo‘shish",
            "projects": "+  Loyiha qo‘shish",
        }
        add_text = add_texts[kind]
        header.addWidget(button(add_text, "primary", self.add))
        root.addLayout(header)

        filters = QFrame()
        filters.setObjectName("surface")
        filter_layout = QHBoxLayout(filters)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(14)
        self.search = QLineEdit()
        placeholders = {
            "employees": "Xodim yoki bo‘limni qidirish...",
            "work_types": "Ish turini qidirish...",
            "departments": "Bo‘limni qidirish...",
            "projects": "Loyiha yoki biriktirilgan xodimni qidirish...",
        }
        self.search.setPlaceholderText(placeholders[kind])
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(280)
        self.search.textChanged.connect(self.load)
        self.department_filter = None
        if kind == "employees":
            self.department_filter = QComboBox()
            self.department_filter.setMinimumWidth(210)
            self.department_filter.setCursor(Qt.PointingHandCursor)
            self.department_filter.currentIndexChanged.connect(self.load)
        self.inactive = QCheckBox(
            "Yakunlanganlarni ko‘rsatish"
            if kind == "projects"
            else "Arxivdagilarni ko‘rsatish"
        )
        self.inactive.toggled.connect(self.load)
        filter_layout.addWidget(self.search)
        if self.department_filter:
            filter_layout.addWidget(self.department_filter)
        filter_layout.addWidget(self.inactive)
        filter_layout.addStretch()
        root.addWidget(filters)

        card = QFrame()
        card.setObjectName("surface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1)
        card_layout.setSpacing(0)

        table_header = QWidget()
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(17, 12, 12, 12)
        table_header_layout.setSpacing(8)
        table_title = QLabel("Ro‘yxat")
        table_title.setObjectName("sectionTitle")
        self.count_label = QLabel()
        self.count_label.setObjectName("sectionMeta")
        table_header_layout.addWidget(table_title)
        table_header_layout.addWidget(self.count_label)
        table_header_layout.addStretch()
        table_header_layout.addWidget(button("Tahrirlash", "secondary", self.edit))
        table_header_layout.addWidget(
            button(
                "Yakunlash / qayta ochish"
                if kind == "projects"
                else "Arxiv / faollashtirish",
                "quiet",
                self.toggle,
            )
        )
        table_header_layout.addWidget(button("O‘chirish", "danger", self.delete))
        card_layout.addWidget(table_header)

        self.table = QTableWidget()
        configure_table(self.table)
        self.table.doubleClicked.connect(self.edit)
        card_layout.addWidget(self.table)
        empty_titles = {
            "employees": "Xodimlar hali yo‘q",
            "work_types": "Ish turlari hali yo‘q",
            "departments": "Bo‘limlar hali yo‘q",
            "projects": "Loyihalar hali yo‘q",
        }
        empty_texts = {
            "employees": "Yuqoridagi “Xodim qo‘shish” tugmasi orqali birinchi xodimni kiriting.",
            "work_types": "Yuqoridagi “Ish turi qo‘shish” tugmasi orqali birinchi turni kiriting.",
            "departments": "Yuqoridagi “Bo‘lim qo‘shish” tugmasi orqali birinchi bo‘limni kiriting.",
            "projects": "Yuqoridagi “Loyiha qo‘shish” tugmasi orqali birinchi loyihani kiriting.",
        }
        empty_title = empty_titles[kind]
        empty_text = empty_texts[kind]
        self.empty_state = EmptyState(empty_title, empty_text)
        card_layout.addWidget(self.empty_state, 1)
        root.addWidget(card, 1)
        self.load()

    def refresh_department_filter(self):
        if not self.department_filter:
            return
        selected_department_id = self.department_filter.currentData()
        departments = sorted(
            self.db.all("departments", True),
            key=lambda department: department["name"].casefold(),
        )
        self.department_filter.blockSignals(True)
        self.department_filter.clear()
        self.department_filter.addItem("Barcha bo‘limlar", None)
        self.department_filter.addItem("Bo‘limsiz", 0)
        for department in departments:
            suffix = " (arxivda)" if not department["is_active"] else ""
            self.department_filter.addItem(
                f'{department["name"]}{suffix}', department["id"]
            )
        selected_index = self.department_filter.findData(selected_department_id)
        self.department_filter.setCurrentIndex(max(0, selected_index))
        self.department_filter.blockSignals(False)

    def load(self):
        self.refresh_department_filter()
        rows = self.db.all(self.kind, self.inactive.isChecked())
        query = self.search.text().strip().casefold()
        self.rows = [
            row for row in rows if query in " ".join(str(value) for value in row).casefold()
        ]
        if self.kind == "employees":
            department_id = self.department_filter.currentData()
            if department_id == 0:
                self.rows = [row for row in self.rows if row["department_id"] is None]
            elif department_id is not None:
                self.rows = [
                    row for row in self.rows if row["department_id"] == department_id
                ]

        headers = {
            "employees": ["№", "XODIM", "BO‘LIM", "LOYIHALARI", "QO‘SHILGAN SANA", "HOLATI"],
            "work_types": ["№", "ISH TURI", "HOLATI"],
            "departments": ["№", "BO‘LIM", "HOLATI"],
            "projects": ["№", "LOYIHA", "XODIMLAR", "BOSHLANGAN", "YAKUNLANGAN", "HOLATI"],
        }[self.kind]
        self.table.clear()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.rows))

        for row_index, row in enumerate(self.rows):
            name = (
                f'{row["first_name"]} {row["last_name"]}'
                if self.kind == "employees"
                else row["name"]
            )
            values = [row_index + 1, name]
            if self.kind == "employees":
                values.append(row["department_name"] or "Bo‘limsiz")
                values.append(row["project_names"] or "Biriktirilmagan")
                created_date = QDate.fromString(row["created_at"][:10], Qt.ISODate)
                values.append(created_date.toString("dd.MM.yyyy"))
            elif self.kind == "projects":
                values.append(row["employee_names"] or "Biriktirilmagan")
                start_date = QDate.fromString(row["start_date"], Qt.ISODate)
                values.append(start_date.toString("dd.MM.yyyy"))
                values.append(
                    QDate.fromString(row["completed_at"], Qt.ISODate).toString("dd.MM.yyyy")
                    if row["completed_at"]
                    else "—"
                )
            values.append(
                "Faol"
                if row["is_active"]
                else ("Yakunlangan" if self.kind == "projects" else "Arxivda")
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, row["id"])
                item.setTextAlignment(Qt.AlignCenter)
                if column == 0:
                    item.setForeground(QColor("#98a2b3"))
                elif column == 1:
                    item.setForeground(QColor("#1d2939"))
                elif column == len(values) - 1:
                    item.setForeground(QColor("#067647" if row["is_active"] else "#98a2b3"))
                    font = item.font()
                    font.setWeight(QFont.DemiBold)
                    item.setFont(font)
                self.table.setItem(row_index, column, item)

        table_header = self.table.horizontalHeader()
        table_header.setStretchLastSection(False)
        table_header.setSectionResizeMode(QHeaderView.Fixed)
        self.resize_table_columns()
        QTimer.singleShot(0, self.resize_table_columns)
        self.count_label.setText(f"{len(self.rows)} ta")
        self.table.setVisible(bool(self.rows))
        self.empty_state.setVisible(not self.rows)

    def resize_table_columns(self):
        if not self.table.columnCount():
            return
        self.table.setColumnWidth(0, self.INDEX_COLUMN_WIDTH)
        available_width = max(
            0, self.table.viewport().width() - self.INDEX_COLUMN_WIDTH
        )
        if self.kind == "employees":
            weights = [0.20, 0.16, 0.28, 0.20, 0.16]
        elif self.kind == "projects":
            weights = [0.24, 0.29, 0.15, 0.16, 0.16]
        else:
            weights = [0.75, 0.25]
        assigned_width = 0
        for offset, weight in enumerate(weights, 1):
            if offset == len(weights):
                width = max(1, available_width - assigned_width)
            else:
                width = max(1, round(available_width * weight))
                assigned_width += width
            self.table.setColumnWidth(offset, width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.resize_table_columns)

    def selected(self):
        index = self.table.currentRow()
        if index < 0:
            QMessageBox.information(
                self, "Qator tanlanmagan", "Avval ro‘yxatdan bitta qatorni tanlang."
            )
            return None
        return self.rows[index]

    def add(self):
        dialog = EntityDialog(self.kind, parent=self, db=self.db)
        if not dialog.exec():
            return
        try:
            actions = {
                "employees": self.db.add_employee,
                "work_types": self.db.add_work_type,
                "departments": self.db.add_department,
                "projects": self.db.add_project,
            }
            action = actions[self.kind]
            action(*dialog.values())
            self.load()
            self.changed.emit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Takroriy nom", "Bu nom oldin kiritilgan.")

    def edit(self, *_):
        row = self.selected()
        if not row:
            return
        dialog = EntityDialog(self.kind, row, self, self.db)
        if not dialog.exec():
            return
        try:
            actions = {
                "employees": self.db.update_employee,
                "work_types": self.db.update_work_type,
                "departments": self.db.update_department,
                "projects": self.db.update_project,
            }
            action = actions[self.kind]
            action(row["id"], *dialog.values())
            self.load()
            self.changed.emit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Takroriy nom", "Bu nom oldin kiritilgan.")

    def toggle(self):
        row = self.selected()
        if not row:
            return
        if self.kind == "projects" and row["is_active"]:
            dialog = ProjectCompletionDialog(row, self)
            if not dialog.exec():
                return
            self.db.complete_project(row["id"], dialog.value())
        elif self.kind == "projects":
            self.db.reopen_project(row["id"])
        else:
            self.db.toggle_active(self.kind, row["id"], not row["is_active"])
        self.load()
        self.changed.emit()

    def delete(self):
        row = self.selected()
        if not row:
            return
        name = (
            f'{row["first_name"]} {row["last_name"]}'
            if self.kind == "employees"
            else row["name"]
        )
        result = QMessageBox.question(
            self,
            "O‘chirishni tasdiqlang",
            f'“{name}” o‘chirilsinmi?\n\n'
            + (
                "Agar hisobotlarda ishlatilgan bo‘lsa, loyiha yakunlanganlar ro‘yxatiga o‘tkaziladi."
                if self.kind == "projects"
                else "Agar hisoblarda ishlatilgan bo‘lsa, arxivga olinadi."
            ),
        )
        if result != QMessageBox.Yes:
            return
        deleted = self.db.delete_if_unused(self.kind, row["id"])
        self.load()
        self.changed.emit()
        message = (
            "Yozuv butunlay o‘chirildi."
            if deleted
            else (
                "Tarixiy ma’lumotlar saqlanishi uchun loyiha yakunlandi."
                if self.kind == "projects"
                else "Tarixiy ma’lumotlar saqlanishi uchun yozuv arxivga olindi."
            )
        )
        QMessageBox.information(self, "Tayyor", message)


class DailyPage(QWidget):
    EMPLOYEE_COLUMN_WIDTH = 190
    PROJECT_COLUMN_WIDTH = 230
    FROZEN_COLUMNS_WIDTH = EMPLOYEE_COLUMN_WIDTH + PROJECT_COLUMN_WIDTH
    WORK_TYPE_COLUMN_WIDTH = 150
    HEADER_HEIGHT = 78

    def __init__(self, db):
        super().__init__()
        self.setObjectName("page")
        self.db = db
        self.loading = False
        self.selected_department_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 27, 34, 30)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        headings = QVBoxLayout()
        headings.setSpacing(4)
        title = QLabel("Kunlik hisob")
        title.setObjectName("title")
        subtitle = QLabel("Katakni tanlang va bajarilgan ishlar sonini klaviaturadan kiriting")
        subtitle.setObjectName("subtitle")
        headings.addWidget(title)
        headings.addWidget(subtitle)
        header.addLayout(headings)
        header.addStretch()

        previous = button("‹", "dateNav", lambda: self.move_date(-1))
        previous.setToolTip("Oldingi kun")
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd.MM.yyyy")
        self.date.setMinimumWidth(126)
        self.date.dateChanged.connect(self.load)
        following = button("›", "dateNav", lambda: self.move_date(1))
        following.setToolTip("Keyingi kun")
        today = button("Bugun", "secondary", self.go_today)
        header.addWidget(previous)
        header.addWidget(self.date)
        header.addWidget(following)
        header.addWidget(today)
        root.addLayout(header)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self.employee_metric = MetricCard("Faol xodimlar")
        self.project_metric = MetricCard("Faol loyihalar")
        self.total_metric = MetricCard("Kunlik jami", accent=True)
        metrics.addWidget(self.employee_metric)
        metrics.addWidget(self.project_metric)
        metrics.addWidget(self.total_metric)
        root.addLayout(metrics)

        card = QFrame()
        card.setObjectName("surface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1)
        card_layout.setSpacing(0)

        self.department_tabs = QTabBar()
        self.department_tabs.setObjectName("departmentTabs")
        self.department_tabs.setExpanding(False)
        self.department_tabs.setUsesScrollButtons(True)
        self.department_tabs.setDocumentMode(True)
        self.department_tabs.currentChanged.connect(self.select_department)
        card_layout.addWidget(self.department_tabs)

        table_header = QWidget()
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(17, 13, 17, 13)
        table_header_layout.setSpacing(8)
        table_title = QLabel("Ishlar jadvali")
        table_title.setObjectName("sectionTitle")
        self.date_label = QLabel()
        self.date_label.setObjectName("sectionMeta")
        self.save_state = QLabel("●  Avtomatik saqlanadi")
        self.save_state.setObjectName("sectionMeta")
        table_header_layout.addWidget(table_title)
        table_header_layout.addWidget(self.date_label)
        table_header_layout.addStretch()
        table_header_layout.addWidget(self.save_state)
        card_layout.addWidget(table_header)

        self.table_container = QWidget()
        table_container_layout = QHBoxLayout(self.table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.setSpacing(0)

        self.employee_table = QTableWidget()
        self.employee_table.setObjectName("frozenEmployees")
        configure_table(self.employee_table)
        self.employee_table.setColumnCount(2)
        self.employee_table.setHorizontalHeaderLabels(["XODIM", "LOYIHA"])
        self.employee_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.employee_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.employee_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.employee_table.setFocusPolicy(Qt.NoFocus)
        self.employee_table.setFixedWidth(self.FROZEN_COLUMNS_WIDTH)

        self.table = QuantityTable()
        configure_table(self.table)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemChanged.connect(self.save)
        self.table.verticalScrollBar().valueChanged.connect(
            self.employee_table.verticalScrollBar().setValue
        )
        self.employee_table.verticalScrollBar().valueChanged.connect(
            self.table.verticalScrollBar().setValue
        )
        table_container_layout.addWidget(self.employee_table)
        table_container_layout.addWidget(self.table, 1)
        card_layout.addWidget(self.table_container)
        self.empty_state = EmptyState(
            "Jadval hali tayyor emas",
            "Tanlangan bo‘limdagi xodimlarga faol loyiha biriktirilganini va ish turi mavjudligini tekshiring.",
        )
        card_layout.addWidget(self.empty_state, 1)
        root.addWidget(card, 1)
        self.load()

    def move_date(self, days):
        self.date.setDate(self.date.date().addDays(days))

    def go_today(self):
        self.date.setDate(QDate.currentDate())

    def refresh_department_tabs(self):
        departments, has_unassigned = self.db.daily_departments()
        tabs = [(department["id"], department["name"]) for department in departments]
        if has_unassigned:
            tabs.append((0, "Bo‘limsiz"))

        self.department_tabs.blockSignals(True)
        while self.department_tabs.count():
            self.department_tabs.removeTab(0)
        for department_id, name in tabs:
            index = self.department_tabs.addTab(name)
            self.department_tabs.setTabData(index, department_id)

        selected_index = next(
            (
                index
                for index in range(self.department_tabs.count())
                if self.department_tabs.tabData(index) == self.selected_department_id
            ),
            0 if self.department_tabs.count() else -1,
        )
        if selected_index >= 0:
            self.department_tabs.setCurrentIndex(selected_index)
            self.selected_department_id = self.department_tabs.tabData(selected_index)
        else:
            self.selected_department_id = None
        self.department_tabs.blockSignals(False)
        self.department_tabs.setVisible(bool(tabs))

    def select_department(self, index):
        if index < 0:
            return
        self.selected_department_id = self.department_tabs.tabData(index)
        self.load()

    @staticmethod
    def work_type_header(name):
        lines = wrap(name.upper(), width=18, break_long_words=True)
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = f'{lines[-1][:15].rstrip()}…'
        return "\n".join(lines)

    def load(self):
        self.loading = True
        self.refresh_department_tabs()
        work_date = self.date.date().toString("yyyy-MM-dd")
        self.assignments, self.types, values = self.db.daily_matrix(
            work_date, self.selected_department_id
        )

        self.employee_table.clearSpans()
        self.employee_table.clear()
        self.employee_table.setColumnCount(2)
        self.employee_table.setHorizontalHeaderLabels(["XODIM", "LOYIHA"])
        self.employee_table.setRowCount(len(self.assignments))

        self.table.clear()
        self.table.setRowCount(len(self.assignments))
        self.table.setColumnCount(len(self.types))
        self.table.setHorizontalHeaderLabels(
            [self.work_type_header(work_type["name"]) for work_type in self.types]
        )
        for column, work_type in enumerate(self.types):
            self.table.horizontalHeaderItem(column).setToolTip(work_type["name"])

        employee_groups = {}
        for row_index, assignment in enumerate(self.assignments):
            employee_groups.setdefault(assignment["employee_id"], []).append(row_index)
            project = QTableWidgetItem(assignment["project_name"])
            project.setFlags(project.flags() & ~Qt.ItemIsEditable)
            project.setForeground(QColor("#344054"))
            project.setToolTip(assignment["project_name"])
            self.employee_table.setItem(row_index, 1, project)
            for column, work_type in enumerate(self.types):
                quantity = values.get(
                    (
                        assignment["employee_id"],
                        assignment["project_id"],
                        work_type["id"],
                    ),
                    0,
                )
                item = QTableWidgetItem(str(quantity))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, column, item)

        for employee_id, group_rows in employee_groups.items():
            first_row = group_rows[0]
            assignment = self.assignments[first_row]
            name = QTableWidgetItem(
                f'{assignment["last_name"]} {assignment["first_name"]}'
            )
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)
            name.setForeground(QColor("#1d2939"))
            name.setBackground(QColor("#f4f7fb"))
            name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.employee_table.setItem(first_row, 0, name)
            if len(group_rows) > 1:
                self.employee_table.setSpan(first_row, 0, len(group_rows), 1)

        table_header = self.table.horizontalHeader()
        table_header.setFixedHeight(self.HEADER_HEIGHT)
        table_header.setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)
        table_header.setSectionResizeMode(QHeaderView.Fixed)
        for column in range(self.table.columnCount()):
            self.table.setColumnWidth(column, self.WORK_TYPE_COLUMN_WIDTH)
        employee_header = self.employee_table.horizontalHeader()
        employee_header.setFixedHeight(self.HEADER_HEIGHT)
        employee_header.setSectionResizeMode(QHeaderView.Fixed)
        self.employee_table.setColumnWidth(0, self.EMPLOYEE_COLUMN_WIDTH)
        self.employee_table.setColumnWidth(1, self.PROJECT_COLUMN_WIDTH - 2)

        self.employee_metric.set_value(len(employee_groups))
        self.project_metric.set_value(
            len({assignment["project_id"] for assignment in self.assignments})
        )
        self.total_metric.set_value(sum(values.values()))
        selected_date = self.date.date()
        self.date_label.setText(
            f"{selected_date.day()}-{UZ_MONTHS[selected_date.month() - 1]}, "
            f"{selected_date.year()}"
        )
        self.save_state.setText("●  Avtomatik saqlanadi")
        self.save_state.setStyleSheet("color: #98a2b3;")
        has_matrix = bool(self.assignments and self.types)
        self.table_container.setVisible(has_matrix)
        self.empty_state.setVisible(not has_matrix)
        self.loading = False

    def save(self, item):
        if self.loading:
            return
        try:
            value = int(item.text() or 0)
        except ValueError:
            value = 0
        value = max(0, value)
        if item.text() != str(value):
            self.loading = True
            item.setText(str(value))
            self.loading = False

        self.db.save_quantity(
            self.assignments[item.row()]["employee_id"],
            self.assignments[item.row()]["project_id"],
            self.types[item.column()]["id"],
            self.date.date().toString("yyyy-MM-dd"),
            value,
        )
        self.update_total()
        self.save_state.setText("✓  Saqlandi")
        self.save_state.setStyleSheet("color: #067647; font-weight: 600;")
        QTimer.singleShot(1600, self.reset_save_state)

    def update_total(self):
        total = 0
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                try:
                    total += int(self.table.item(row, column).text())
                except (AttributeError, ValueError):
                    pass
        self.total_metric.set_value(total)

    def reset_save_state(self):
        self.save_state.setText("●  Avtomatik saqlanadi")
        self.save_state.setStyleSheet("color: #98a2b3;")


class StatisticsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.setObjectName("page")
        self.db = db
        self.employee_rows = []
        self.chart_employee_rows = []
        self.selected_employee_id = None
        self.selected_department_id = None
        self.selected_project_id = None
        self.selected_work_type_id = None
        self.employee_bar_sets = []
        self.period_employee_work = []
        self.work_types = []
        self.daily_days = []
        self.daily_day_totals = []
        self.daily_all_totals = []
        self.daily_work_type_totals = {}
        self.daily_number_of_days = 0
        self.departments = []
        self.projects = []
        self.chart_tooltip = QLabel(self, Qt.ToolTip | Qt.WindowTransparentForInput)
        self.chart_tooltip.setObjectName("chartTooltip")
        self.chart_tooltip.setTextFormat(Qt.PlainText)
        self.chart_tooltip.setAttribute(Qt.WA_ShowWithoutActivating)
        self.chart_tooltip.setAttribute(Qt.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 27, 34, 26)
        root.setSpacing(14)

        headings = QVBoxLayout()
        headings.setSpacing(4)
        title = QLabel("Statistika")
        title.setObjectName("title")
        subtitle = QLabel("Tanlangan davr bo‘yicha jamoa natijalarini tahlil qiling")
        subtitle.setObjectName("subtitle")
        headings.addWidget(title)
        headings.addWidget(subtitle)
        root.addLayout(headings)

        filters = QFrame()
        filters.setObjectName("surface")
        filter_root = QVBoxLayout(filters)
        filter_root.setContentsMargins(16, 10, 16, 9)
        filter_root.setSpacing(8)
        date_filter_layout = QHBoxLayout()
        date_filter_layout.setSpacing(12)

        today = QDate.currentDate()
        self.date_from = CalendarDateEdit(today.addDays(-29))
        self.date_to = CalendarDateEdit(today)
        self.date_from.dateChanged.connect(self.date_filter_changed)
        self.date_to.dateChanged.connect(self.date_filter_changed)

        from_box = QVBoxLayout()
        from_box.setSpacing(4)
        from_label = QLabel("Boshlanish sanasi")
        from_label.setObjectName("fieldLabel")
        from_box.addWidget(from_label)
        from_box.addWidget(self.date_from)

        to_box = QVBoxLayout()
        to_box.setSpacing(4)
        to_label = QLabel("Tugash sanasi")
        to_label.setObjectName("fieldLabel")
        to_box.addWidget(to_label)
        to_box.addWidget(self.date_to)

        date_filter_layout.addLayout(from_box)
        separator = QLabel("—")
        separator.setObjectName("muted")
        date_filter_layout.addWidget(separator, 0, Qt.AlignBottom)
        date_filter_layout.addLayout(to_box)
        date_filter_layout.addStretch()
        filter_root.addLayout(date_filter_layout)

        selection_filter_layout = QHBoxLayout()
        selection_filter_layout.setSpacing(12)

        department_filter_box = QVBoxLayout()
        department_filter_box.setSpacing(4)
        department_filter_label = QLabel("Bo‘lim")
        department_filter_label.setObjectName("fieldLabel")
        department_filter_box.addWidget(department_filter_label)

        self.department_combo = QComboBox()
        self.department_combo.setMinimumWidth(190)
        self.department_combo.setCursor(Qt.PointingHandCursor)
        department_filter_box.addWidget(self.department_combo)
        selection_filter_layout.addLayout(department_filter_box, 1)

        project_filter_box = QVBoxLayout()
        project_filter_box.setSpacing(4)
        project_filter_label = QLabel("Loyiha")
        project_filter_label.setObjectName("fieldLabel")
        project_filter_box.addWidget(project_filter_label)
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(210)
        self.project_combo.setCursor(Qt.PointingHandCursor)
        project_filter_box.addWidget(self.project_combo)
        selection_filter_layout.addLayout(project_filter_box, 1)

        work_filter_box = QVBoxLayout()
        work_filter_box.setSpacing(4)
        work_filter_label = QLabel("Ish turi")
        work_filter_label.setObjectName("fieldLabel")
        work_filter_box.addWidget(work_filter_label)

        self.work_type_combo = QComboBox()
        self.work_type_combo.setMinimumWidth(245)
        self.work_type_combo.setCursor(Qt.PointingHandCursor)
        work_filter_box.addWidget(self.work_type_combo)
        selection_filter_layout.addLayout(work_filter_box, 1)

        show_button = button("Natijani ko‘rsatish", "primary", self.load)
        selection_filter_layout.addWidget(show_button, 0, Qt.AlignBottom)
        filter_root.addLayout(selection_filter_layout)
        root.addWidget(filters)

        self.work_type_combo.currentIndexChanged.connect(self.select_work_type)
        self.department_combo.currentIndexChanged.connect(self.select_department)
        self.project_combo.currentIndexChanged.connect(self.select_project)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self.total_metric = MetricCard("Jami bajarilgan ish", accent=True)
        self.employee_metric = MetricCard("Ishlagan xodimlar")
        self.day_metric = MetricCard("Davrdagi kunlar")
        metrics.addWidget(self.total_metric)
        metrics.addWidget(self.employee_metric)
        metrics.addWidget(self.day_metric)
        root.addLayout(metrics)

        (
            employee_card,
            self.employee_stack,
            self.employee_chart_page,
            self.employee_chart,
            self.employee_empty,
            _,
        ) = self.create_chart_card(
            "Xodimlar natijasi",
            "Ustunga bosing — xodimning kunlik tafsilotlari pastda ochiladi",
            "Bu davrda bajarilgan ishlar yo‘q",
            "Boshqa sana oralig‘ini tanlang yoki kunlik hisobga ma’lumot kiriting.",
            scrollable=True,
            vertical_scrollable=True,
        )
        root.addWidget(employee_card, 1)

        (
            daily_card,
            self.daily_stack,
            self.daily_chart_page,
            self.daily_chart,
            self.daily_empty,
            self.selection_chip,
        ) = self.create_chart_card(
            "Kunma-kun natijalar",
            "Nuqta ustiga olib boring — kunlik jami va ishlar tafsiloti ko‘rinadi",
            "Xodim tanlanmagan",
            "Yuqoridagi chartdan xodim ustunini tanlang.",
            with_selection=True,
            scrollable=True,
        )
        root.addWidget(daily_card, 1)
        for view in (self.employee_chart, self.daily_chart):
            view.viewport().installEventFilter(self)
        self.load()

    @staticmethod
    def create_chart_card(
        title,
        subtitle,
        empty_title,
        empty_text,
        with_selection=False,
        scrollable=False,
        vertical_scrollable=False,
    ):
        card = QFrame()
        card.setObjectName("surface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1)
        card_layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(17, 10, 14, 7)
        header_layout.setSpacing(10)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        description = QLabel(subtitle)
        description.setObjectName("sectionMeta")
        title_box.addWidget(heading)
        title_box.addWidget(description)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        selection = None
        if with_selection:
            selection = QLabel("Xodim tanlanmagan")
            selection.setObjectName("selectionChip")
            header_layout.addWidget(selection)
        card_layout.addWidget(header)

        stack = QStackedWidget()
        stack.setMinimumHeight(160)
        chart_view = QChartView()
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMouseTracking(True)
        chart_view.setStyleSheet("background: transparent; border: 0;")
        chart_view.setMinimumHeight(160)
        chart_page = chart_view
        if scrollable:
            chart_page = QScrollArea()
            chart_page.setFrameShape(QFrame.NoFrame)
            chart_page.setWidgetResizable(False)
            chart_page.setVerticalScrollBarPolicy(
                Qt.ScrollBarAsNeeded if vertical_scrollable else Qt.ScrollBarAlwaysOff
            )
            chart_page.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff if vertical_scrollable else Qt.ScrollBarAsNeeded
            )
            chart_page.setWidget(chart_view)
            chart_page.setStyleSheet("QScrollArea { background: transparent; border: 0; }")
        empty = EmptyState(empty_title, empty_text)
        stack.addWidget(chart_page)
        stack.addWidget(empty)
        card_layout.addWidget(stack, 1)
        return card, stack, chart_page, chart_view, empty, selection

    def date_filter_changed(self, *_):
        if self.date_from.date() <= self.date_to.date():
            self.load()

    def load(self):
        if self.date_from.date() > self.date_to.date():
            QMessageBox.information(
                self,
                "Sana oralig‘ini tekshiring",
                "Boshlanish sanasi tugash sanasidan keyin bo‘lishi mumkin emas.",
            )
            return
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        self.rebuild_department_combo()
        self.rebuild_project_combo()
        work_type_rows = self.db.statistics_work_types(
            date_from, date_to, self.selected_department_id, self.selected_project_id
        )
        self.work_types = [
            {
                "id": row["id"],
                "name": row["name"],
                "total": int(row["total"]),
            }
            for row in work_type_rows
        ]
        valid_work_type_ids = {work_type["id"] for work_type in self.work_types}
        if self.selected_work_type_id not in valid_work_type_ids:
            self.selected_work_type_id = None

        self.period_employee_work = [
            {
                "employee_id": row["employee_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "department_id": row["department_id"],
                "work_type_id": row["work_type_id"],
                "total": int(row["total"]),
            }
            for row in self.db.employee_work_type_totals(
                date_from, date_to, self.selected_department_id, self.selected_project_id
            )
        ]
        self.rebuild_work_type_combo()
        self.apply_work_type_filter()

    def rebuild_department_combo(self):
        self.departments = list(self.db.all("departments", True))
        valid_department_ids = {department["id"] for department in self.departments}
        if self.selected_department_id not in valid_department_ids:
            self.selected_department_id = None

        self.department_combo.blockSignals(True)
        self.department_combo.clear()
        self.department_combo.addItem("Barcha bo‘limlar", None)
        for department in sorted(
            self.departments, key=lambda department: department["name"].casefold()
        ):
            suffix = " (arxivda)" if not department["is_active"] else ""
            self.department_combo.addItem(
                f'{department["name"]}{suffix}', department["id"]
            )
        selected_index = self.department_combo.findData(self.selected_department_id)
        self.department_combo.setCurrentIndex(max(0, selected_index))
        self.department_combo.blockSignals(False)

    def select_department(self, _index):
        self.selected_department_id = self.department_combo.currentData()
        self.load()

    def rebuild_project_combo(self):
        self.projects = list(self.db.all("projects", True))
        valid_project_ids = {project["id"] for project in self.projects}
        if self.selected_project_id not in valid_project_ids:
            self.selected_project_id = None
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("Barcha loyihalar", None)
        for project in sorted(self.projects, key=lambda item: item["name"].casefold()):
            suffix = " (yakunlangan)" if not project["is_active"] else ""
            self.project_combo.addItem(f'{project["name"]}{suffix}', project["id"])
        selected_index = self.project_combo.findData(self.selected_project_id)
        self.project_combo.setCurrentIndex(max(0, selected_index))
        self.project_combo.blockSignals(False)

    def select_project(self, _index):
        self.selected_project_id = self.project_combo.currentData()
        self.load()

    def rebuild_work_type_combo(self):
        self.work_type_combo.blockSignals(True)
        self.work_type_combo.clear()
        self.work_type_combo.addItem("Barchasi — barcha ishlar", None)
        for work_type in self.work_types:
            self.work_type_combo.addItem(
                f'{work_type["name"]} — {work_type["total"]} ta', work_type["id"]
            )
        selected_index = self.work_type_combo.findData(self.selected_work_type_id)
        self.work_type_combo.setCurrentIndex(max(0, selected_index))
        self.work_type_combo.blockSignals(False)

    def select_work_type(self, _index):
        self.selected_work_type_id = self.work_type_combo.currentData()
        self.apply_work_type_filter()

    def apply_work_type_filter(self):
        self.chart_tooltip.hide()
        employees = {}
        for row in self.period_employee_work:
            if (
                self.selected_work_type_id is not None
                and row["work_type_id"] != self.selected_work_type_id
            ):
                continue
            employee = employees.setdefault(
                row["employee_id"],
                {
                    "id": row["employee_id"],
                    "name": f'{row["first_name"]} {row["last_name"]}',
                    "total": 0,
                    "work_values": {},
                },
            )
            employee["work_values"][row["work_type_id"]] = row["total"]
            employee["total"] += row["total"]

        self.employee_rows = sorted(
            employees.values(), key=lambda employee: (-employee["total"], employee["name"])
        )

        self.total_metric.set_value(sum(row["total"] for row in self.employee_rows))
        self.employee_metric.set_value(len(self.employee_rows))
        self.day_metric.set_value(self.date_from.date().daysTo(self.date_to.date()) + 1)

        if not self.employee_rows:
            self.selected_employee_id = None
            self.employee_stack.setCurrentWidget(self.employee_empty)
            self.daily_stack.setCurrentWidget(self.daily_empty)
            self.selection_chip.setText("Xodim tanlanmagan")
            return

        employee_ids = [row["id"] for row in self.employee_rows]
        if self.selected_employee_id not in employee_ids:
            self.selected_employee_id = employee_ids[0]
        self.render_employee_chart()
        self.render_daily_chart()

    @staticmethod
    def new_chart():
        chart = QChart()
        chart.legend().hide()
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        chart.setLocale(QLocale("uz_UZ"))
        chart.setMargins(QMargins(9, 5, 16, 7))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(450)
        return chart

    @staticmethod
    def replace_chart(view, chart):
        old_chart = view.chart()
        view.setChart(chart)
        if old_chart and old_chart is not chart:
            old_chart.deleteLater()

    @staticmethod
    def axis_top(maximum):
        padding = max(1, (maximum + 9) // 10)
        padded = maximum + padding
        return max(4, ((padded + 3) // 4) * 4)

    @staticmethod
    def style_value_axis(axis):
        axis.setLabelsColor(QColor("#667085"))
        axis.setLabelsFont(QFont("Segoe UI", 9))
        axis.setLabelFormat("%.0f")
        axis.setGridLinePen(QPen(QColor("#eaecf0"), 1))
        axis.setLinePen(QPen(QColor("#d0d5dd"), 1))
        axis.setTickCount(5)

    def render_employee_chart(self):
        chart = self.new_chart()
        self.chart_employee_rows = list(reversed(self.employee_rows))
        values = [row["total"] for row in self.chart_employee_rows]
        names = [row["name"] for row in self.chart_employee_rows]

        bar_set = QBarSet("Jami")
        bar_set.append(values)
        bar_set.setColor(QColor("#2f6fed"))
        bar_set.setBorderColor(QColor("#255dcc"))
        bar_set.setSelectedColor(QColor("#2f6fed"))
        bar_set.setLabelColor(QColor("#344054"))
        bar_set.setLabelFont(QFont("Segoe UI", 8, QFont.DemiBold))
        bar_set.clicked.connect(self.employee_clicked)
        bar_set.hovered.connect(self.employee_hovered)
        self.employee_bar_sets = [bar_set]

        series = QHorizontalBarSeries()
        series.append(bar_set)
        series.setBarWidth(0.58)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        series.setLabelsPosition(QAbstractBarSeries.LabelsOutsideEnd)
        chart.addSeries(series)

        name_axis = QBarCategoryAxis()
        name_axis.append(names)
        name_axis.setTruncateLabels(False)
        name_axis.setLabelsColor(QColor("#344054"))
        name_axis.setLabelsFont(QFont("Segoe UI", 9, QFont.DemiBold))
        name_axis.setGridLineVisible(False)
        name_axis.setLinePen(QPen(QColor("#d0d5dd"), 1))

        value_axis = QValueAxis()
        value_axis.setRange(
            0, self.axis_top(max(row["total"] for row in self.chart_employee_rows))
        )
        self.style_value_axis(value_axis)

        chart.addAxis(name_axis, Qt.AlignLeft)
        chart.addAxis(value_axis, Qt.AlignBottom)
        series.attachAxis(name_axis)
        series.attachAxis(value_axis)
        self.replace_chart(self.employee_chart, chart)
        self.employee_stack.setCurrentWidget(self.employee_chart_page)
        QTimer.singleShot(0, self.update_employee_chart_size)

        selected_index = next(
            index
            for index, row in enumerate(self.chart_employee_rows)
            if row["id"] == self.selected_employee_id
        )
        for bar_set in self.employee_bar_sets:
            bar_set.selectBar(selected_index)

    def update_employee_chart_size(self):
        if not isinstance(self.employee_chart_page, QScrollArea):
            return
        viewport = self.employee_chart_page.viewport()
        required_width = max(1, viewport.width())
        required_height = max(
            max(160, viewport.height()),
            85 + len(self.chart_employee_rows) * 36,
        )
        self.employee_chart.setFixedSize(required_width, required_height)

    def employee_clicked(self, index):
        if not 0 <= index < len(self.chart_employee_rows):
            return
        self.selected_employee_id = self.chart_employee_rows[index]["id"]
        for bar_set in self.employee_bar_sets:
            bar_set.deselectAllBars()
            bar_set.selectBar(index)
        self.render_daily_chart()

    def employee_hovered(self, status, index):
        if status and 0 <= index < len(self.chart_employee_rows):
            row = self.chart_employee_rows[index]
            lines = [
                row["name"],
                f'{self.current_work_type_name()}: {row["total"]} ta',
            ]
            if self.selected_work_type_id is None:
                for work_type in self.work_types:
                    quantity = row["work_values"].get(work_type["id"], 0)
                    if quantity > 0:
                        lines.append(f'{work_type["name"]}: {quantity} ta')
            self.show_chart_tooltip("\n".join(lines))
        else:
            self.chart_tooltip.hide()

    def show_chart_tooltip(self, text):
        self.chart_tooltip.setText(text)
        self.chart_tooltip.adjustSize()
        cursor = QCursor.pos()
        screen = QApplication.screenAt(cursor) or self.screen()
        bounds = screen.availableGeometry()
        x = cursor.x() + 16
        y = cursor.y() + 20
        if x + self.chart_tooltip.width() > bounds.right() + 1:
            x = cursor.x() - self.chart_tooltip.width() - 16
        if y + self.chart_tooltip.height() > bounds.bottom() + 1:
            y = cursor.y() - self.chart_tooltip.height() - 20
        self.chart_tooltip.move(max(bounds.left(), x), max(bounds.top(), y))
        self.chart_tooltip.show()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Leave:
            self.chart_tooltip.hide()
        return super().eventFilter(watched, event)

    def hideEvent(self, event):
        self.chart_tooltip.hide()
        super().hideEvent(event)

    def selected_employee(self):
        return next(
            row for row in self.employee_rows if row["id"] == self.selected_employee_id
        )

    def current_work_type_name(self):
        if self.selected_work_type_id is None:
            return "Barcha ishlar"
        return next(
            work_type["name"]
            for work_type in self.work_types
            if work_type["id"] == self.selected_work_type_id
        )

    def render_daily_chart(self):
        employee = self.selected_employee()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        records = self.db.employee_daily_work_types(
            employee["id"], date_from, date_to, self.selected_project_id
        )

        selected_date = self.date_from.date()
        number_of_days = selected_date.daysTo(self.date_to.date()) + 1
        self.daily_days = [selected_date.addDays(offset) for offset in range(number_of_days)]
        day_keys = [day.toString("yyyy-MM-dd") for day in self.daily_days]

        all_totals_by_date = {}
        work_type_totals_by_date = {}
        for row in records:
            quantity = int(row["total"])
            all_totals_by_date[row["work_date"]] = (
                all_totals_by_date.get(row["work_date"], 0) + quantity
            )
            type_totals = work_type_totals_by_date.setdefault(row["work_type_id"], {})
            type_totals[row["work_date"]] = type_totals.get(row["work_date"], 0) + quantity

        self.daily_all_totals = [
            int(all_totals_by_date.get(day_key, 0)) for day_key in day_keys
        ]
        self.daily_work_type_totals = {
            work_type["id"]: [
                int(work_type_totals_by_date.get(work_type["id"], {}).get(day_key, 0))
                for day_key in day_keys
            ]
            for work_type in self.work_types
        }
        self.daily_day_totals = (
            self.daily_all_totals
            if self.selected_work_type_id is None
            else self.daily_work_type_totals[self.selected_work_type_id]
        )
        self.daily_number_of_days = number_of_days

        chart = self.new_chart()
        series = QLineSeries()
        series.setName(self.current_work_type_name())
        series.setPen(QPen(QColor("#2f6fed"), 3))
        series.setColor(QColor("#2f6fed"))
        series.setPointsVisible(True)
        series.setPointLabelsColor(QColor("#344054"))
        series.setPointLabelsFont(QFont("Segoe UI", 8, QFont.DemiBold))
        series.setPointLabelsFormat("@yPoint")
        series.setPointLabelsVisible(number_of_days <= 14)
        date_times = []
        for day, value in zip(self.daily_days, self.daily_day_totals):
            moment = QDateTime(day, QTime(12, 0))
            date_times.append(moment)
            series.append(moment.toMSecsSinceEpoch(), value)
        series.hovered.connect(self.daily_point_hovered)
        chart.addSeries(series)

        date_axis = QDateTimeAxis()
        if number_of_days == 1:
            date_axis.setRange(
                date_times[0].addSecs(-12 * 60 * 60),
                date_times[0].addSecs(12 * 60 * 60),
            )
        else:
            date_axis.setRange(date_times[0], date_times[-1])
        date_axis.setFormat(
            "dd MMM"
            if number_of_days <= 31
            else "dd.MM"
            if number_of_days <= 120
            else "MMM yy"
        )
        date_axis.setTickCount(min(7, max(2, number_of_days)))
        date_axis.setLabelsColor(QColor("#667085"))
        date_axis.setLabelsFont(QFont("Segoe UI", 8))
        date_axis.setGridLineVisible(False)
        date_axis.setLinePen(QPen(QColor("#d0d5dd"), 1))

        value_axis = QValueAxis()
        value_axis.setRange(0, self.axis_top(max(self.daily_day_totals, default=0)))
        self.style_value_axis(value_axis)

        chart.addAxis(date_axis, Qt.AlignBottom)
        chart.addAxis(value_axis, Qt.AlignLeft)
        series.attachAxis(date_axis)
        series.attachAxis(value_axis)
        self.replace_chart(self.daily_chart, chart)
        self.selection_chip.setText(employee["name"])
        self.daily_stack.setCurrentWidget(self.daily_chart_page)
        QTimer.singleShot(0, self.update_daily_chart_size)

    def update_daily_chart_size(self):
        if not isinstance(self.daily_chart_page, QScrollArea):
            return
        viewport_width = max(1, self.daily_chart_page.viewport().width())
        required_width = (
            viewport_width
            if self.daily_number_of_days <= 45
            else max(viewport_width, 130 + self.daily_number_of_days * 22)
        )
        required_height = max(150, self.daily_chart_page.height() - 12)
        self.daily_chart.setFixedSize(required_width, required_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_employee_chart_size)
        QTimer.singleShot(0, self.update_daily_chart_size)

    def daily_point_hovered(self, point, status):
        if not status:
            self.chart_tooltip.hide()
            return
        day = QDateTime.fromMSecsSinceEpoch(round(point.x())).date()
        index = self.date_from.date().daysTo(day)
        if not 0 <= index < len(self.daily_days):
            self.chart_tooltip.hide()
            return
        self.show_chart_tooltip(self.daily_tooltip_text(index))

    def daily_tooltip_text(self, index):
        employee = self.selected_employee()
        day = self.daily_days[index]
        lines = [
            employee["name"],
            day.toString("dd.MM.yyyy"),
            "",
            f"Barcha ishlar: {self.daily_all_totals[index]} ta",
        ]
        if self.selected_work_type_id is None:
            for work_type in self.work_types:
                quantity = self.daily_work_type_totals[work_type["id"]][index]
                if quantity > 0:
                    lines.append(f'{work_type["name"]}: {quantity} ta')
        else:
            lines.append(
                f'{self.current_work_type_name()}: {self.daily_day_totals[index]} ta'
            )
        return "\n".join(lines)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("HR Control")
        self.resize(1220, 760)
        self.setMinimumSize(960, 620)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar_collapsed = False
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(238)
        self.nav_layout = QVBoxLayout(self.sidebar)
        self.nav_layout.setContentsMargins(18, 22, 18, 18)
        self.nav_layout.setSpacing(7)

        identity = QHBoxLayout()
        identity.setSpacing(11)
        self.logo = QFrame()
        self.logo.setObjectName("logoMark")
        self.logo.setFixedSize(40, 40)
        logo_layout = QVBoxLayout(self.logo)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_text = QLabel("HC")
        logo_text.setObjectName("logoText")
        logo_text.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_text)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(1)
        self.brand = QLabel("HR Control")
        self.brand.setObjectName("brand")
        self.brand_sub = QLabel("ISH NAZORATI")
        self.brand_sub.setObjectName("brandSub")
        brand_box.addWidget(self.brand)
        brand_box.addWidget(self.brand_sub)
        identity.addWidget(self.logo)
        identity.addLayout(brand_box)
        identity.addStretch()
        self.sidebar_toggle = button("‹", "sidebarToggle", self.toggle_sidebar)
        self.sidebar_toggle.setFixedSize(32, 32)
        self.sidebar_toggle.setToolTip("Yon menyuni yopish")
        identity.addWidget(self.sidebar_toggle, 0, Qt.AlignVCenter)
        self.nav_layout.addLayout(identity)
        self.nav_layout.addSpacing(27)

        self.nav_section = QLabel("ASOSIY MENYU")
        self.nav_section.setObjectName("navSection")
        self.nav_section.setContentsMargins(12, 0, 0, 3)
        self.nav_layout.addWidget(self.nav_section)

        self.stack = QStackedWidget()
        self.daily = DailyPage(self.db)
        self.employees = CrudPage(self.db, "employees")
        self.departments = CrudPage(self.db, "departments")
        self.projects = CrudPage(self.db, "projects")
        self.types = CrudPage(self.db, "work_types")
        self.statistics = StatisticsPage(self.db)
        for page in (
            self.statistics,
            self.daily,
            self.employees,
            self.departments,
            self.projects,
            self.types,
        ):
            self.stack.addWidget(page)

        self.buttons = []
        self.nav_items = (
            ("▥", "Statistika"),
            ("▦", "Kunlik hisob"),
            ("♙", "Xodimlar"),
            ("▣", "Bo‘limlar"),
            ("◆", "Loyihalar"),
            ("✓", "Ish turlari"),
        )
        for index, (icon, label) in enumerate(self.nav_items):
            nav_button = button(f"{icon}   {label}", "nav")
            nav_button.setMinimumHeight(44)
            nav_button.clicked.connect(
                lambda checked=False, page_index=index: self.navigate(page_index)
            )
            self.nav_layout.addWidget(nav_button)
            self.buttons.append(nav_button)

        self.nav_layout.addStretch()
        self.sidebar_line = QFrame()
        self.sidebar_line.setObjectName("sidebarLine")
        self.nav_layout.addWidget(self.sidebar_line)
        self.nav_layout.addSpacing(8)
        self.sidebar_foot = QLabel("Ma’lumotlar ushbu qurilmada\nxavfsiz saqlanadi  ·  v1.0")
        self.sidebar_foot.setObjectName("sidebarFoot")
        self.nav_layout.addWidget(self.sidebar_foot)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

        self.employees.changed.connect(self.daily.load)
        self.departments.changed.connect(self.employees.load)
        self.departments.changed.connect(self.daily.load)
        self.projects.changed.connect(self.employees.load)
        self.projects.changed.connect(self.daily.load)
        self.employees.changed.connect(self.projects.load)
        self.types.changed.connect(self.daily.load)
        self.navigate(0)

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar.setFixedWidth(76 if self.sidebar_collapsed else 238)
        margins = (10, 22, 10, 18) if self.sidebar_collapsed else (18, 22, 18, 18)
        self.nav_layout.setContentsMargins(*margins)
        for widget in (
            self.logo,
            self.brand,
            self.brand_sub,
            self.nav_section,
            self.sidebar_foot,
        ):
            widget.setVisible(not self.sidebar_collapsed)
        self.sidebar_toggle.setText("›" if self.sidebar_collapsed else "‹")
        self.sidebar_toggle.setToolTip(
            "Yon menyuni ochish" if self.sidebar_collapsed else "Yon menyuni yopish"
        )
        for nav_button, (icon, label) in zip(self.buttons, self.nav_items):
            nav_button.setText(icon if self.sidebar_collapsed else f"{icon}   {label}")
            nav_button.setToolTip(label if self.sidebar_collapsed else "")
            nav_button.setProperty("collapsed", self.sidebar_collapsed)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for button_index, nav_button in enumerate(self.buttons):
            nav_button.setProperty("active", button_index == index)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)
        if index == 0:
            self.statistics.load()
        elif index == 1:
            self.daily.load()


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "HRControl.Desktop.1"
            )
        except (AttributeError, OSError):
            pass
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLE)
    app_icon = QIcon(str(resource_path("assets/hr-control-app-icon.png")))
    app.setWindowIcon(app_icon)
    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())
