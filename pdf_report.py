from pathlib import Path

from PySide6.QtCore import QMarginsF, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QPen,
)


ACCENT = QColor("#4f46e5")
INK = QColor("#000000")
TEXT = QColor("#202020")
MUTED = QColor("#505050")
BORDER = QColor("#707070")
SOFT = QColor("#ffffff")
ACCENT_SOFT = QColor("#ffffff")


def _font(size, bold=False):
    font = QFont("Segoe UI", size)
    if bold:
        font.setWeight(QFont.DemiBold)
    return font


def _text(painter, rect, value, size=9, color=TEXT, bold=False, flags=None):
    painter.setFont(_font(size, bold))
    painter.setPen(color)
    if flags is None:
        flags = Qt.AlignLeft | Qt.AlignVCenter
    painter.drawText(QRectF(rect), int(flags), str(value))


def _elided(painter, value, width):
    metrics = QFontMetrics(painter.font(), painter.device())
    return metrics.elidedText(str(value), Qt.ElideRight, max(1, int(width)))


def _rounded_box(painter, rect, fill=QColor("#ffffff"), border=BORDER, radius=0):
    painter.setPen(QPen(border, 1))
    painter.setBrush(fill)
    painter.drawRoundedRect(QRectF(rect), radius, radius)


def _page_header(painter, width, title, metadata, page_number, total_pages):
    _text(painter, QRectF(0, 0, width, 46), title, 21, INK, True)
    _text(painter, QRectF(0, 47, width, 30), metadata, 8, MUTED)
    _text(
        painter,
        QRectF(width - 160, 0, 160, 30),
        f"{page_number} / {total_pages}",
        8,
        MUTED,
        flags=Qt.AlignRight | Qt.AlignVCenter,
    )


def _page_footer(painter, width, height):
    painter.setPen(QPen(BORDER, 1))
    painter.drawLine(QPointF(0, height - 24), QPointF(width, height - 24))
    _text(painter, QRectF(0, height - 22, width, 20), "HR Control", 7, MUTED)


def _draw_summary(painter, width, y, rows, date_count):
    total = sum(int(row[-1]) for row in rows) if rows else 0
    employees = len({str(row[0]) for row in rows})
    projects = len({str(row[1]) for row in rows})
    values = (
        ("ХОДИМЛАР", employees),
        ("ЖИНОИЙ ИШЛАР", projects),
        ("ДАВРДАГИ КУНЛАР", date_count),
        ("ЖАМИ ИШ", total),
    )
    gap = 10
    box_width = (width - gap * 3) / 4
    for index, (label, value) in enumerate(values):
        rect = QRectF(index * (box_width + gap), y, box_width, 68)
        _rounded_box(
            painter,
            rect,
            QColor("#ffffff"),
            BORDER,
            0,
        )
        _text(painter, QRectF(rect.x() + 14, rect.y() + 8, rect.width() - 28, 20), label, 7, MUTED, True)
        _text(
            painter,
            QRectF(rect.x() + 14, rect.y() + 29, rect.width() - 28, 30),
            value,
            16,
            INK,
            True,
        )


def _column_widths(width, column_count):
    if column_count <= 2:
        return [width / max(1, column_count)] * column_count
    fixed = width * 0.38
    numeric_width = (width - fixed) / (column_count - 2)
    return [width * 0.20, width * 0.18] + [numeric_width] * (column_count - 2)


def _draw_table(painter, width, y, height, headers, rows, continuation=False):
    if continuation:
        _text(painter, QRectF(0, y - 28, width, 24), "ЖАДВАЛ ДАВОМИ", 10, INK, True)
    column_widths = _column_widths(width, len(headers))
    header_font_size = 5 if len(headers) <= 10 else 4
    header_text_flags = Qt.AlignCenter | Qt.AlignVCenter | Qt.TextWrapAnywhere
    header_height = 46
    row_height = min(32, max(20, (height - header_height) / max(1, len(rows))))
    employee_spans = {}
    row_index = 0
    while row_index < len(rows):
        span = 1
        while (
            row_index + span < len(rows)
            and str(rows[row_index + span][0]) == str(rows[row_index][0])
        ):
            span += 1
        employee_spans[row_index] = span
        row_index += span
    x = 0
    for header, column_width in zip(headers, column_widths):
        rect = QRectF(x, y, column_width, header_height)
        painter.fillRect(rect, QColor("#ffffff"))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRect(rect)
        _text(
            painter,
            rect.adjusted(5, 3, -5, -3),
            header,
            header_font_size,
            QColor("#000000"),
            True,
            header_text_flags,
        )
        x += column_width

    for row_index, row in enumerate(rows):
        x = 0
        top = y + header_height + row_index * row_height
        for column_index, (value, column_width) in enumerate(zip(row, column_widths)):
            if column_index == 0 and row_index not in employee_spans:
                x += column_width
                continue
            cell_height = (
                row_height * employee_spans[row_index]
                if column_index == 0
                else row_height
            )
            rect = QRectF(x, top, column_width, cell_height)
            painter.fillRect(rect, QColor("#ffffff"))
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.drawRect(rect)
            painter.setFont(_font(7, column_index == len(row) - 1))
            shown = _elided(painter, value, column_width - 12)
            _text(
                painter,
                rect.adjusted(6, 0, -6, 0),
                shown,
                7,
                TEXT,
                column_index == len(row) - 1,
                Qt.AlignCenter | Qt.AlignVCenter,
            )
            x += column_width


def _nice_top(maximum):
    maximum = max(1, int(maximum))
    step = max(1, (maximum + 4) // 5)
    return step * 5


def _draw_line_chart(painter, rect, labels, values):
    _rounded_box(painter, rect, radius=14)
    _text(
        painter,
        QRectF(rect.x() + 20, rect.y() + 12, rect.width() - 40, 28),
        "ТАНЛАНГАН КУНЛАР БЎЙИЧА ЖАМИ ИШЛАР",
        11,
        INK,
        True,
    )
    plot = rect.adjusted(58, 58, -24, -46)
    maximum = _nice_top(max(values, default=0))
    for tick in range(6):
        value = maximum * tick / 5
        y = plot.bottom() - plot.height() * tick / 5
        painter.setPen(QPen(BORDER, 1))
        painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
        _text(
            painter,
            QRectF(rect.x() + 8, y - 10, 42, 20),
            str(round(value)),
            7,
            MUTED,
            flags=Qt.AlignRight | Qt.AlignVCenter,
        )
    if not values:
        _text(painter, plot, "Маълумот мавжуд эмас", 10, MUTED, flags=Qt.AlignCenter)
        return
    count = len(values)
    points = []
    for index, value in enumerate(values):
        x = plot.center().x() if count == 1 else plot.left() + plot.width() * index / (count - 1)
        y = plot.bottom() - plot.height() * value / maximum
        points.append(QPointF(x, y))
    painter.setPen(QPen(ACCENT, 3))
    for first, second in zip(points, points[1:]):
        painter.drawLine(first, second)
    painter.setBrush(QColor("#ffffff"))
    for point in points:
        painter.setPen(QPen(ACCENT, 3))
        painter.drawEllipse(point, 4, 4)
    label_step = max(1, (count + 6) // 7)
    for index, (label, point) in enumerate(zip(labels, points)):
        if index % label_step == 0 or index == count - 1:
            _text(
                painter,
                QRectF(point.x() - 40, plot.bottom() + 7, 80, 20),
                label,
                7,
                MUTED,
                flags=Qt.AlignCenter,
            )


def _draw_employee_chart(painter, rect, employees):
    _rounded_box(painter, rect, radius=14)
    shown = sorted(employees, key=lambda item: (-item[1], item[0]))[:14]
    suffix = " (энг юқори 14)" if len(employees) > len(shown) else ""
    _text(
        painter,
        QRectF(rect.x() + 20, rect.y() + 12, rect.width() - 40, 28),
        f"ХОДИМЛАР КЕСИМИДАГИ ЖАМИ ИШЛАР{suffix}",
        11,
        INK,
        True,
    )
    plot = rect.adjusted(170, 53, -34, -22)
    if not shown:
        _text(painter, plot, "Маълумот мавжуд эмас", 10, MUTED, flags=Qt.AlignCenter)
        return
    maximum = _nice_top(max(value for _, value in shown))
    gap = 5
    bar_height = max(11, (plot.height() - gap * (len(shown) - 1)) / len(shown))
    for index, (name, value) in enumerate(shown):
        y = plot.y() + index * (bar_height + gap)
        _text(
            painter,
            QRectF(rect.x() + 16, y, 145, bar_height),
            _elided(painter, name, 140),
            7,
            TEXT,
            flags=Qt.AlignRight | Qt.AlignVCenter,
        )
        background = QRectF(plot.x(), y, plot.width(), bar_height)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#f7f8fc"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(background, 5, 5)
        bar = QRectF(plot.x(), y, max(2, plot.width() * value / maximum), bar_height)
        painter.setPen(Qt.NoPen)
        painter.setBrush(ACCENT)
        painter.drawRoundedRect(bar, 5, 5)
        _text(
            painter,
            QRectF(plot.x() + 6, y, plot.width() - 12, bar_height),
            str(value),
            7,
            QColor("#ffffff") if bar.width() > 35 else INK,
            True,
            Qt.AlignLeft | Qt.AlignVCenter,
        )


def write_period_pdf(
    path,
    title,
    metadata,
    headers,
    rows,
    daily_labels,
    daily_totals,
    employee_totals,
    date_count,
):
    """Create a landscape PDF with a table first and charts on page two."""
    path = Path(path)
    writer = QPdfWriter(str(path))
    writer.setResolution(144)
    writer.setTitle(title)
    writer.setCreator("HR Control")
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Landscape,
            QMarginsF(9, 9, 9, 9),
            QPageLayout.Millimeter,
        )
    )
    painter = QPainter(writer)
    if not painter.isActive():
        raise OSError(f"PDF файлини яратиб бўлмади: {path}")

    width, height = writer.width(), writer.height()
    first_page_rows = 25
    chunks = [rows[:first_page_rows]]
    remaining = rows[first_page_rows:]
    while remaining:
        chunks.append(remaining[:31])
        remaining = remaining[31:]
    total_pages = len(chunks) + 1

    try:
        painter.fillRect(QRectF(0, 0, width, height), QColor("#ffffff"))
        _page_header(painter, width, title, metadata, 1, total_pages)
        _draw_summary(painter, width, 88, rows, date_count)
        _draw_table(painter, width, 174, height - 214, headers, chunks[0])
        if len(chunks) > 1:
            _text(
                painter,
                QRectF(0, height - 48, width, 20),
                "Жадвалнинг қолган қисми кейинги саҳифада давом этади.",
                7,
                MUTED,
                flags=Qt.AlignRight | Qt.AlignVCenter,
            )
        _page_footer(painter, width, height)

        for page_index, chunk in enumerate(chunks[1:], 2):
            writer.newPage()
            painter.fillRect(QRectF(0, 0, width, height), QColor("#ffffff"))
            _page_header(painter, width, title, metadata, page_index, total_pages)
            _draw_table(
                painter,
                width,
                110,
                height - 150,
                headers,
                chunk,
                continuation=True,
            )
            _page_footer(painter, width, height)

        chart_page = len(chunks) + 1
        writer.newPage()
        painter.fillRect(QRectF(0, 0, width, height), QColor("#ffffff"))
        _page_header(
            painter, width, "ДИАГРАММАЛАР", metadata, chart_page, total_pages
        )
        available = height - 126
        gap = 18
        chart_height = (available - gap) / 2
        _draw_line_chart(
            painter,
            QRectF(0, 88, width, chart_height),
            daily_labels,
            daily_totals,
        )
        _draw_employee_chart(
            painter,
            QRectF(0, 88 + chart_height + gap, width, chart_height),
            employee_totals,
        )
        _page_footer(painter, width, height)
    finally:
        painter.end()
