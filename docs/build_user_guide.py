"""Capture the current UI with an in-memory demo database and build an Uzbek PDF."""

import os
import sqlite3
import sys
from html import escape
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_SCALE_FACTOR", "2")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QDate, QMarginsF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QIcon, QImage, QPageLayout, QPageSize,
    QPainter, QPdfWriter, QTextDocument,
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from main import EntityDialog, MainWindow, STYLE

OUTPUT = ROOT / "docs" / "user-guide"
SHOTS = OUTPUT / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
PDF = ROOT / "dist" / "instruction.pdf"
PDF.parent.mkdir(exist_ok=True)

app = QApplication([])
for font_file in ("segoeui.ttf", "segoeuib.ttf"):
    QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts") / font_file))
app.setStyle("Fusion")
app.setFont(QFont("Segoe UI", 10))
app.setStyleSheet(STYLE)
app.setWindowIcon(QIcon(str(ROOT / "assets/hr-control-app-icon.png")))

# Reuse the app's schema while keeping the user's database completely untouched.
connect = sqlite3.connect
with patch("database.app_data_dir", return_value=OUTPUT), patch(
    "database.sqlite3.connect", side_effect=lambda *_a, **_k: connect(":memory:")
):
    window = MainWindow()
db = window.db
for first, last in [
    ("Aziz", "Karimov"), ("Malika", "Rahimova"), ("Javohir", "Aliyev"),
    ("Dilnoza", "Ismoilova"), ("Nigora", "Tursunova"), ("Sardor", "Nazarov"),
]:
    db.add_employee(first, last)
for row in db.all("employees"):
    db.connection.execute(
        "UPDATE employees SET created_at=? WHERE id=?",
        (f'2026-09-0{row["id"]} 09:30:00', row["id"]),
    )
db.connection.commit()
db.toggle_active("employees", 6, False)
for name in [
    "Hisobot tayyorlash", "Hujjat tekshirish", "Ariza qabul qilish", "Mijoz bilan ishlash",
    "Ma’lumot kiritish", "Shartnoma tayyorlash", "Qo‘ng‘iroq qilish", "Hujjatlarni arxivlash",
]:
    db.add_work_type(name)
for day in range(2, 9):
    for employee in range(1, 6):
        for work_type in range(1, 5):
            quantity = (employee * 3 + day * 2 + work_type) % 9 + 1
            db.save_quantity(employee, work_type, f"2026-09-{day:02d}", quantity)
window.employees.load()
window.types.load()
window.daily.date.setDate(QDate(2026, 9, 8))
stats = window.statistics
stats.date_from.setDate(QDate(2026, 9, 2))
stats.date_to.setDate(QDate(2026, 9, 8))
window.resize(1280, 800)
window.show()


def settle():
    app.processEvents()
    QTest.qWait(550)


def capture(name, widget, rect=None):
    settle()
    shot = widget.grab(rect) if rect is not None else widget.grab()
    path = SHOTS / f"{name}.png"
    assert shot.save(str(path)), path
    return path


window.navigate(0)
capture("01-overview", window)
window.navigate(2)
capture("02-employees", window.employees, QRect(0, 0, window.employees.width(), 560))
dialog = EntityDialog("employees", parent=window)
dialog.first.setText("Umid")
dialog.last.setText("Sobirov")
dialog.show()
capture("03-add-employee", dialog)
dialog.close()
window.navigate(3)
capture("04-work-types", window.types, QRect(0, 0, window.types.width(), 680))
dialog = EntityDialog("work_types", parent=window)
dialog.name.setText("Buyurtma tayyorlash")
dialog.show()
capture("05-add-work-type", dialog)
dialog.close()
window.navigate(1)
window.daily.table.setCurrentCell(0, 1)
QTest.keyClicks(window.daily.table, "7")
capture("06-daily", window)
window.daily.table.horizontalScrollBar().setValue(window.daily.table.horizontalScrollBar().maximum())
capture("07-daily-scroll", window.daily.table)
window.navigate(0)
stats.load()
capture("08-statistics", window)
stats.work_type_combo.setCurrentIndex(stats.work_type_combo.findData(1))
capture("09-filtered", window)
stats.work_type_combo.setCurrentIndex(0)
settle()
capture("10-employee-chart", stats.employee_stack.parentWidget())
index = next(i for i, row in enumerate(stats.chart_employee_rows) if row["id"] == stats.selected_employee_id)
stats.employee_hovered(True, index)
capture("11-employee-hover", stats.chart_tooltip)
stats.chart_tooltip.hide()
capture("12-daily-chart", stats.daily_stack.parentWidget())
stats.daily_point_hovered(stats.daily_chart.chart().series()[0].at(6), True)
capture("13-daily-hover", stats.chart_tooltip)
stats.chart_tooltip.hide()
window.navigate(2)
window.employees.inactive.setChecked(True)
window.employees.table.setCurrentCell(0, 0)
capture("14-archive", window.employees, QRect(0, 0, window.employees.width(), 600))


class Guide:
    WIDTH, HEIGHT = 1400, 990

    def __init__(self):
        self.writer = QPdfWriter(str(PDF))
        self.writer.setPageLayout(QPageLayout(
            QPageSize(QPageSize.A4), QPageLayout.Landscape, QMarginsF(0, 0, 0, 0)
        ))
        self.writer.setResolution(144)
        self.writer.setTitle("HR Control — foydalanish qo‘llanmasi")
        self.writer.setCreator("HR Control")
        self.painter = QPainter(self.writer)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.painter.setRenderHint(QPainter.SmoothPixmapTransform)
        self.painter.setWindow(0, 0, self.WIDTH, self.HEIGHT)
        self.number = 0

    def text(self, x, y, width, content, size=23, color="#344054", max_height=None):
        doc = QTextDocument()
        doc.setDocumentMargin(0)
        doc.setDefaultFont(QFont("Segoe UI"))
        doc.setDefaultStyleSheet(
            f"body {{font-family: 'Segoe UI'; font-size: {size}px; color: {color};}} "
            "p {margin: 0 0 10px 0;} b {font-weight: 700;}"
        )
        doc.setHtml(f"<body>{content}</body>")
        doc.setTextWidth(width)
        if max_height is not None:
            assert doc.size().height() <= max_height, (self.number, content, doc.size().height(), max_height)
        self.painter.save()
        self.painter.translate(x, y)
        doc.drawContents(self.painter)
        self.painter.restore()
        return doc.size().height()

    def rect(self, x, y, w, h, color, radius=14):
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(QColor(color))
        self.painter.drawRoundedRect(QRectF(x, y, w, h), radius, radius)

    def page(self, title, subtitle):
        if self.number:
            self.writer.newPage()
        self.number += 1
        self.painter.fillRect(QRectF(0, 0, 1400, 990), QColor("#ffffff"))
        self.rect(60, 42, 44, 34, "#2f6fed", 8)
        self.text(67, 46, 40, "HC", 20, "#ffffff")
        self.text(116, 45, 1100, "HR CONTROL  /  FOYDALANISH QO‘LLANMASI", 19, "#667085")
        self.text(60, 94, 1280, escape(title), 39, "#101828", 60)
        self.text(60, 152, 1280, subtitle, 22, "#667085", 62)
        self.painter.fillRect(QRectF(60, 938, 1280, 1), QColor("#e4e7ec"))
        self.text(60, 954, 1180, "08.09.2026  ·  O‘zbekcha qo‘llanma  ·  Rasmlarda namunaviy ma’lumotlar", 16, "#98a2b3")
        self.text(1270, 950, 70, f"{self.number:02d} / 08", 19, "#667085")

    def image(self, name, x, y, width, height):
        image = QImage(str(SHOTS / f"{name}.png"))
        assert not image.isNull(), name
        ratio = min(width / image.width(), height / image.height())
        w, h = image.width() * ratio, image.height() * ratio
        self.rect(x - 3, y - 3, w + 6, h + 6, "#e4e7ec", 4)
        self.painter.drawImage(QRectF(x, y, w, h), image)
        return h

    def note(self, x, y, width, title, text, height=130):
        self.rect(x, y, width, height, "#f2f6ff")
        self.text(x + 20, y + 15, width - 40, title, 23, "#2459c4", 38)
        self.text(x + 20, y + 53, width - 40, text, 20, max_height=height - 60)

    def finish(self):
        self.painter.end()


guide = Guide()
guide.page("HR Control bilan ishni boshlash", "Xodimlar bajargan ishlarni kiriting va natijalarni sana hamda ish turi bo‘yicha kuzating.")
guide.image("01-overview", 250, 210, 900, 562)
guide.note(60, 815, 410, "1. Ro‘yxatlarni tayyorlang", "Xodimlar va ish turlarini qo‘shing.", 104)
guide.note(495, 815, 410, "2. Kunlik hisobni kiriting", "Sanani tanlab, kataklarga son yozing.", 104)
guide.note(930, 815, 410, "3. Natijalarni ko‘ring", "Statistikada davr va ish turini tanlang.", 104)
guide.text(60, 785, 1280, "Ochish: <b>HR-Control.exe</b> faylini ikki marta bosing. Bo‘limlar chap menyuda joylashgan.", 22)

guide.page("Xodim qo‘shish va ro‘yxatdan topish", "Chap menyudan <b>Xodimlar</b> bo‘limini oching. Yangi xodimlar ro‘yxatning yuqorisida turadi.")
guide.image("02-employees", 60, 220, 835, 460)
guide.image("03-add-employee", 935, 240, 390, 400)
guide.text(60, 710, 820,
    "<p><b>1.</b> <b>+ Xodim qo‘shish</b> tugmasini bosing.</p>"
    "<p><b>2.</b> Ism va familiyani to‘ldirib, <b>Saqlash</b>ni bosing.</p>"
    "<p><b>3.</b> Qidiruv maydoniga ism yoki familiya yozib xodimni toping.</p>", 24, max_height=195)
guide.note(935, 685, 405, "Qo‘shilgan sana", "Sana avtomatik yoziladi va <b>08.09.2026</b> ko‘rinishida chiqadi. Ro‘yxat yangi IDdan eski IDga tartiblangan.", 212)

guide.page("Ish turlarini tayyorlash", "Chap menyudan <b>Ish turlari</b> bo‘limini oching. Bu nomlar Kunlik hisobda ustunlarga aylanadi.")
guide.image("04-work-types", 60, 220, 820, 505)
guide.image("05-add-work-type", 935, 245, 390, 320)
guide.text(935, 605, 405,
    "<p><b>1.</b> <b>+ Ish turi qo‘shish</b>ni bosing.</p>"
    "<p><b>2.</b> Ish turining nomini kiriting.</p>"
    "<p><b>3.</b> <b>Saqlash</b>ni bosing.</p>", 24, max_height=225)
guide.note(60, 775, 820, "Ro‘yxat tartibi", "Yangi qo‘shilgan ish turi tepada turadi. Bir xil nomni qayta kiritib bo‘lmaydi; mavjud nomni qidiruvdan tekshiring.", 132)

guide.page("Kunlik hisob: sana va miqdor", "<b>1.</b> Sanani tanlang.  <b>2.</b> Xodim va ish turi kesishgan katakni bosing.  <b>3.</b> Sonni klaviaturadan kiriting.")
guide.image("06-daily", 235, 210, 930, 582)
guide.note(60, 805, 625, "Sana boshqaruvi", "‹ / › — oldingi yoki keyingi kun. <b>Bugun</b> — bugungi sana.", 118)
guide.note(710, 805, 630, "Avtomatik saqlash", "Qiymat kiritilganda <b>Saqlandi</b> yozuvi chiqadi.", 118)

guide.page("Son kiritish va gorizontal scroll", "Ustunlar ko‘payganda jadvalni o‘ngga suring: ular siqilmaydi, pastda gorizontal scroll paydo bo‘ladi.")
guide.image("07-daily-scroll", 210, 215, 980, 510)
guide.note(60, 752, 410, "Shift + g‘ildirak", "Kursor jadval ustida bo‘lsin. <b>Shift</b>ni bosib, sichqoncha g‘ildiragini aylantiring — o‘ngga/chapga suriladi.", 172)
guide.note(495, 752, 410, "Qiymatni almashtirish", "Katakni tanlab yangi sonni ketma-ket yozing. <b>Delete</b> — nol qilish; <b>Backspace</b> — oxirgi raqamni o‘chirish.", 172)
guide.note(930, 752, 410, "Yana ikki usul", "Pastdagi scroll tutqichini torting. Ustun chegarasini tortib kengligini o‘zgartiring. Oddiy g‘ildirak — yuqoriga/pastga.", 172)

guide.page("Statistika: davr va ish turi", "<b>1.</b> Sana oralig‘ini belgilang.  <b>2.</b> <b>Natijani ko‘rsatish</b>ni bosing.  <b>3.</b> Kerakli ish turini tanlang.")
guide.image("09-filtered", 235, 210, 930, 582)
guide.note(60, 805, 625, "Barchasi yoki bitta ish turi", "<b>Barchasi</b> jami natijani, tanlangan tur esa o‘sha ish sonini ko‘rsatadi.", 118)
guide.note(710, 805, 630, "Xodimni tanlash", "Yuqoridagi xodim ustunini bosing — pastda uning kunlik natijalari ochiladi.", 118)

guide.page("Chartdagi hover tafsilotlari", "Hover — kursorni ustun yoki nuqta ustiga olib borish. Kursor shu yerda turguncha ma’lumot ochiq qoladi.")
guide.text(60, 222, 1000, "1. Xodim ustuni: tanlangan davr bo‘yicha jami va ish turlari", 25, "#101828")
guide.image("10-employee-chart", 60, 273, 915, 240)
guide.image("11-employee-hover", 1020, 286, 300, 224)
guide.text(60, 550, 1000, "2. Kunlik nuqta: tanlangan sanadagi jami va ishlar tafsiloti", 25, "#101828")
guide.image("12-daily-chart", 60, 602, 915, 240)
guide.image("13-daily-hover", 1020, 614, 300, 255)
guide.text(60, 886, 1280, "Kursorni olib chiqsangiz hover yopiladi. Ish turi filtrlanganda shu tur natijasi ko‘rsatiladi.", 22)

guide.page("Tahrirlash, arxiv va ma’lumotlarni saqlash", "Xodimlar hamda ish turlari bo‘limlarida avval kerakli qatorni tanlang, keyin tegishli tugmani bosing.")
guide.image("14-archive", 60, 215, 720, 435)
guide.text(830, 220, 510,
    "<p><b>Tahrirlash</b><br>Tanlangan yozuvning nomini o‘zgartirib saqlang. Qatorni ikki marta bosish ham tahrir oynasini ochadi.</p>"
    "<p><b>Arxiv / faollashtirish</b><br>Arxivdagi yozuv Kunlik hisobdan yashiriladi. Uni ko‘rish uchun <b>Arxivdagilarni ko‘rsatish</b>ni belgilang.</p>"
    "<p><b>O‘chirish</b><br>Hisoblarda ishlatilgan yozuv arxivlanadi; ishlatilmagan yozuv tasdiqdan keyin butunlay o‘chiriladi.</p>", 23, max_height=454)
guide.note(60, 705, 1280, "Zaxira nusxa olish", "Dasturni yoping. <b>Win + R</b>ni bosib <b>%LOCALAPPDATA%\\HR Control</b> manzilini oching. "
    "Ichidagi <b>hr_control.db</b> faylidan boshqa papka yoki tashqi xotiraga nusxa oling. Bu .exe orqali ishlatiladigan dastur bazasidir.", 136)
guide.text(60, 864, 1280, "<b>Jadval bo‘sh bo‘lsa:</b> kamida bitta faol xodim va ish turi borligini tekshiring. "
    "<b>Statistika bo‘sh bo‘lsa:</b> hisob kiritilgan sana oralig‘ini tanlang.", 23, max_height=65)
guide.finish()
window.close()
db.connection.close()

# Render every page for a visual review and ensure the PDF contains readable text.
pdf = QPdfDocument()
assert pdf.load(str(PDF)) == QPdfDocument.Error.None_
assert pdf.pageCount() == 8, pdf.pageCount()
for page in range(pdf.pageCount()):
    assert pdf.getAllText(page).text().strip(), page
    preview = pdf.render(page, QSize(1400, 990))
    assert preview.save(str(OUTPUT / f"page-{page + 1:02d}.png"))
pdf.close()
print(f"GUIDE_OK: {PDF} (8 pages, {PDF.stat().st_size:,} bytes)")
