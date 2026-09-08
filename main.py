import sqlite3
import sys
from pathlib import Path

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
    QAbstractItemView,
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
QHeaderView::section {
    background: #f9fafb;
    color: #667085;
    border: 0;
    border-bottom: 1px solid #eaecf0;
    padding: 11px 12px;
    font-size: 11px;
    font-weight: 700;
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
        if row >= 0 and column > 0:
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
    def __init__(self, kind, row=None, parent=None):
        super().__init__(parent)
        self.kind = kind
        noun = "Xodim" if kind == "employees" else "Ish turi"
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
        else:
            self.name = self.add_field(root, "Ish turi nomi *", row["name"] if row else "")

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
            valid = self.first.text().strip() and self.last.text().strip()
        else:
            valid = self.name.text().strip()
        if valid:
            self.accept()
            return
        QMessageBox.warning(self, "Majburiy maydon", "Majburiy maydonlarni to‘ldiring.")

    def values(self):
        if self.kind == "employees":
            return self.first.text().strip(), self.last.text().strip()
        return (self.name.text().strip(),)


class CrudPage(QWidget):
    changed = Signal()

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
        title = QLabel("Xodimlar" if kind == "employees" else "Ish turlari")
        title.setObjectName("title")
        subtitle = QLabel(
            "Jamoa a’zolari va ularning holatini boshqaring"
            if kind == "employees"
            else "Kunlik hisobda ishlatiladigan ish turlarini boshqaring"
        )
        subtitle.setObjectName("subtitle")
        headings.addWidget(title)
        headings.addWidget(subtitle)
        header.addLayout(headings)
        header.addStretch()
        add_text = "+  Xodim qo‘shish" if kind == "employees" else "+  Ish turi qo‘shish"
        header.addWidget(button(add_text, "primary", self.add))
        root.addLayout(header)

        filters = QFrame()
        filters.setObjectName("surface")
        filter_layout = QHBoxLayout(filters)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(14)
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Xodimni qidirish..." if kind == "employees" else "Ish turini qidirish..."
        )
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(280)
        self.search.textChanged.connect(self.load)
        self.inactive = QCheckBox("Arxivdagilarni ko‘rsatish")
        self.inactive.toggled.connect(self.load)
        filter_layout.addWidget(self.search)
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
        table_header_layout.addWidget(button("Arxiv / faollashtirish", "quiet", self.toggle))
        table_header_layout.addWidget(button("O‘chirish", "danger", self.delete))
        card_layout.addWidget(table_header)

        self.table = QTableWidget()
        configure_table(self.table)
        self.table.doubleClicked.connect(self.edit)
        card_layout.addWidget(self.table)
        empty_title = "Xodimlar hali yo‘q" if kind == "employees" else "Ish turlari hali yo‘q"
        empty_text = (
            "Yuqoridagi “Xodim qo‘shish” tugmasi orqali birinchi xodimni kiriting."
            if kind == "employees"
            else "Yuqoridagi “Ish turi qo‘shish” tugmasi orqali birinchi turni kiriting."
        )
        self.empty_state = EmptyState(empty_title, empty_text)
        card_layout.addWidget(self.empty_state, 1)
        root.addWidget(card, 1)
        self.load()

    def load(self):
        rows = self.db.all(self.kind, self.inactive.isChecked())
        query = self.search.text().strip().casefold()
        self.rows = [
            row for row in rows if query in " ".join(str(value) for value in row).casefold()
        ]

        headers = (
            ["XODIM", "QO‘SHILGAN SANA", "HOLATI"]
            if self.kind == "employees"
            else ["ISH TURI", "HOLATI"]
        )
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
            values = [name]
            if self.kind == "employees":
                created_date = QDate.fromString(row["created_at"][:10], Qt.ISODate)
                values.append(created_date.toString("dd.MM.yyyy"))
            values.append("Faol" if row["is_active"] else "Arxivda")
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, row["id"])
                if column == 0:
                    item.setForeground(QColor("#1d2939"))
                elif column == len(values) - 1:
                    item.setForeground(QColor("#067647" if row["is_active"] else "#98a2b3"))
                    font = item.font()
                    font.setWeight(QFont.DemiBold)
                    item.setFont(font)
                self.table.setItem(row_index, column, item)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, len(headers)):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)
        self.count_label.setText(f"{len(self.rows)} ta")
        self.table.setVisible(bool(self.rows))
        self.empty_state.setVisible(not self.rows)

    def selected(self):
        index = self.table.currentRow()
        if index < 0:
            QMessageBox.information(
                self, "Qator tanlanmagan", "Avval ro‘yxatdan bitta qatorni tanlang."
            )
            return None
        return self.rows[index]

    def add(self):
        dialog = EntityDialog(self.kind, parent=self)
        if not dialog.exec():
            return
        try:
            action = self.db.add_employee if self.kind == "employees" else self.db.add_work_type
            action(*dialog.values())
            self.load()
            self.changed.emit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Takroriy nom", "Bu nom oldin kiritilgan.")

    def edit(self, *_):
        row = self.selected()
        if not row:
            return
        dialog = EntityDialog(self.kind, row, self)
        if not dialog.exec():
            return
        try:
            action = self.db.update_employee if self.kind == "employees" else self.db.update_work_type
            action(row["id"], *dialog.values())
            self.load()
            self.changed.emit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Takroriy nom", "Bu nom oldin kiritilgan.")

    def toggle(self):
        row = self.selected()
        if not row:
            return
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
            f'“{name}” o‘chirilsinmi?\n\nAgar hisoblarda ishlatilgan bo‘lsa, arxivga olinadi.',
        )
        if result != QMessageBox.Yes:
            return
        deleted = self.db.delete_if_unused(self.kind, row["id"])
        self.load()
        self.changed.emit()
        message = (
            "Yozuv butunlay o‘chirildi."
            if deleted
            else "Tarixiy ma’lumotlar saqlanishi uchun yozuv arxivga olindi."
        )
        QMessageBox.information(self, "Tayyor", message)


class DailyPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.setObjectName("page")
        self.db = db
        self.loading = False

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
        self.type_metric = MetricCard("Ish turlari")
        self.total_metric = MetricCard("Kunlik jami", accent=True)
        metrics.addWidget(self.employee_metric)
        metrics.addWidget(self.type_metric)
        metrics.addWidget(self.total_metric)
        root.addLayout(metrics)

        card = QFrame()
        card.setObjectName("surface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(1, 1, 1, 1)
        card_layout.setSpacing(0)

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

        self.table = QuantityTable()
        configure_table(self.table)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.horizontalHeader().setMinimumSectionSize(160)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemChanged.connect(self.save)
        card_layout.addWidget(self.table)
        self.empty_state = EmptyState(
            "Jadval hali tayyor emas",
            "Hisobni boshlash uchun kamida bitta xodim va bitta ish turi qo‘shing.",
        )
        card_layout.addWidget(self.empty_state, 1)
        root.addWidget(card, 1)
        self.load()

    def move_date(self, days):
        self.date.setDate(self.date.date().addDays(days))

    def go_today(self):
        self.date.setDate(QDate.currentDate())

    def load(self):
        self.loading = True
        work_date = self.date.date().toString("yyyy-MM-dd")
        self.employees, self.types, values = self.db.daily_matrix(work_date)

        self.table.clear()
        self.table.setRowCount(len(self.employees))
        self.table.setColumnCount(len(self.types) + 1)
        self.table.setHorizontalHeaderLabels(
            ["XODIM"] + [work_type["name"].upper() for work_type in self.types]
        )

        for row_index, employee in enumerate(self.employees):
            name = QTableWidgetItem(f'{employee["last_name"]} {employee["first_name"]}')
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)
            name.setForeground(QColor("#1d2939"))
            name.setBackground(QColor("#f9fafb"))
            self.table.setItem(row_index, 0, name)

            for column, work_type in enumerate(self.types, 1):
                quantity = values.get((employee["id"], work_type["id"]), 0)
                item = QTableWidgetItem(str(quantity))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, column, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, max(220, self.table.columnWidth(0)))

        self.employee_metric.set_value(len(self.employees))
        self.type_metric.set_value(len(self.types))
        self.total_metric.set_value(sum(values.values()))
        selected_date = self.date.date()
        self.date_label.setText(
            f"{selected_date.day()}-{UZ_MONTHS[selected_date.month() - 1]}, "
            f"{selected_date.year()}"
        )
        self.save_state.setText("●  Avtomatik saqlanadi")
        self.save_state.setStyleSheet("color: #98a2b3;")
        has_matrix = bool(self.employees and self.types)
        self.table.setVisible(has_matrix)
        self.empty_state.setVisible(not has_matrix)
        self.loading = False

    def save(self, item):
        if self.loading or item.column() == 0:
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
            self.employees[item.row()]["id"],
            self.types[item.column() - 1]["id"],
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
            for column in range(1, self.table.columnCount()):
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
        self.selected_work_type_id = None
        self.employee_bar_sets = []
        self.period_employee_work = []
        self.work_types = []
        self.daily_days = []
        self.daily_day_totals = []
        self.daily_all_totals = []
        self.daily_work_type_totals = {}
        self.daily_number_of_days = 0
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
        self.date_from = QDateEdit(today.addDays(-29))
        self.date_to = QDateEdit(today)
        for control in (self.date_from, self.date_to):
            control.setCalendarPopup(True)
            control.setDisplayFormat("dd.MM.yyyy")
            control.setMinimumWidth(132)

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

        work_filter_box = QVBoxLayout()
        work_filter_box.setSpacing(4)
        work_filter_label = QLabel("Ish turi")
        work_filter_label.setObjectName("fieldLabel")
        work_filter_box.addWidget(work_filter_label)

        self.work_type_combo = QComboBox()
        self.work_type_combo.setMinimumWidth(245)
        self.work_type_combo.setCursor(Qt.PointingHandCursor)
        work_filter_box.addWidget(self.work_type_combo)
        date_filter_layout.addLayout(work_filter_box, 1)

        show_button = button("Natijani ko‘rsatish", "primary", self.load)
        date_filter_layout.addWidget(show_button, 0, Qt.AlignBottom)
        filter_root.addLayout(date_filter_layout)
        root.addWidget(filters)

        self.date_from.dateChanged.connect(self.sync_date_from)
        self.date_to.dateChanged.connect(self.sync_date_to)
        self.work_type_combo.currentIndexChanged.connect(self.select_work_type)

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
            chart_page.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            chart_page.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            chart_page.setWidget(chart_view)
            chart_page.setStyleSheet("QScrollArea { background: transparent; border: 0; }")
        empty = EmptyState(empty_title, empty_text)
        stack.addWidget(chart_page)
        stack.addWidget(empty)
        card_layout.addWidget(stack, 1)
        return card, stack, chart_page, chart_view, empty, selection

    def sync_date_from(self, selected_date):
        if selected_date > self.date_to.date():
            self.date_to.setDate(selected_date)

    def sync_date_to(self, selected_date):
        if selected_date < self.date_from.date():
            self.date_from.setDate(selected_date)

    def load(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        work_type_rows = self.db.statistics_work_types(date_from, date_to)
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
                "work_type_id": row["work_type_id"],
                "total": int(row["total"]),
            }
            for row in self.db.employee_work_type_totals(date_from, date_to)
        ]
        self.rebuild_work_type_combo()
        self.apply_work_type_filter()

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

        selected_index = next(
            index
            for index, row in enumerate(self.chart_employee_rows)
            if row["id"] == self.selected_employee_id
        )
        for bar_set in self.employee_bar_sets:
            bar_set.selectBar(selected_index)

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
            employee["id"], date_from, date_to
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

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(238)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(18, 22, 18, 18)
        nav.setSpacing(7)

        identity = QHBoxLayout()
        identity.setSpacing(11)
        logo = QFrame()
        logo.setObjectName("logoMark")
        logo.setFixedSize(40, 40)
        logo_layout = QVBoxLayout(logo)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_text = QLabel("HC")
        logo_text.setObjectName("logoText")
        logo_text.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_text)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(1)
        brand = QLabel("HR Control")
        brand.setObjectName("brand")
        brand_sub = QLabel("ISH NAZORATI")
        brand_sub.setObjectName("brandSub")
        brand_box.addWidget(brand)
        brand_box.addWidget(brand_sub)
        identity.addWidget(logo)
        identity.addLayout(brand_box)
        identity.addStretch()
        nav.addLayout(identity)
        nav.addSpacing(27)

        section = QLabel("ASOSIY MENYU")
        section.setObjectName("navSection")
        section.setContentsMargins(12, 0, 0, 3)
        nav.addWidget(section)

        self.stack = QStackedWidget()
        self.daily = DailyPage(self.db)
        self.employees = CrudPage(self.db, "employees")
        self.types = CrudPage(self.db, "work_types")
        self.statistics = StatisticsPage(self.db)
        for page in (self.statistics, self.daily, self.employees, self.types):
            self.stack.addWidget(page)

        self.buttons = []
        labels = ("Statistika", "Kunlik hisob", "Xodimlar", "Ish turlari")
        for index, label in enumerate(labels):
            nav_button = button(label, "nav")
            nav_button.setMinimumHeight(44)
            nav_button.clicked.connect(
                lambda checked=False, page_index=index: self.navigate(page_index)
            )
            nav.addWidget(nav_button)
            self.buttons.append(nav_button)

        nav.addStretch()
        line = QFrame()
        line.setObjectName("sidebarLine")
        nav.addWidget(line)
        nav.addSpacing(8)
        foot = QLabel("Ma’lumotlar ushbu qurilmada\nxavfsiz saqlanadi  ·  v1.0")
        foot.setObjectName("sidebarFoot")
        nav.addWidget(foot)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)

        self.employees.changed.connect(self.daily.load)
        self.types.changed.connect(self.daily.load)
        self.navigate(0)

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
