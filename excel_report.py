from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


def _column_name(index):
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _text_cell(reference, value, style=0):
    return (
        f'<c r="{reference}" s="{style}" t="inlineStr">'
        f'<is><t>{escape(str(value))}</t></is></c>'
    )


def _number_cell(reference, value, style=0):
    return f'<c r="{reference}" s="{style}"><v>{int(value)}</v></c>'


def write_period_report(path, title, metadata, headers, rows):
    """Write a styled, dependency-free XLSX report."""
    path = Path(path)
    last_column = _column_name(len(headers))
    sheet_rows = [
        f'<row r="1" ht="28" customHeight="1">{_text_cell("A1", title, 1)}</row>',
        f'<row r="2" ht="22" customHeight="1">{_text_cell("A2", metadata, 2)}</row>',
    ]
    header_cells = "".join(
        _text_cell(f"{_column_name(column)}4", header, 3)
        for column, header in enumerate(headers, 1)
    )
    sheet_rows.append(f'<row r="4" ht="42" customHeight="1">{header_cells}</row>')
    for row_index, values in enumerate(rows, 5):
        cells = []
        for column, value in enumerate(values, 1):
            reference = f"{_column_name(column)}{row_index}"
            cells.append(
                _text_cell(reference, value, 4)
                if column <= 2
                else _number_cell(reference, value, 5)
            )
        sheet_rows.append(f'<row r="{row_index}" ht="22" customHeight="1">{"".join(cells)}</row>')

    columns = [
        '<col min="1" max="1" width="28" customWidth="1"/>',
        '<col min="2" max="2" width="32" customWidth="1"/>',
    ]
    if len(headers) > 2:
        columns.append(f'<col min="3" max="{len(headers)}" width="18" customWidth="1"/>')
    last_row = max(4, len(rows) + 4)
    worksheet = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<dimension ref="A1:{last_column}{last_row}"/>
<sheetViews><sheetView workbookViewId="0"><pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
<cols>{''.join(columns)}</cols><sheetData>{''.join(sheet_rows)}</sheetData>
<autoFilter ref="A4:{last_column}{last_row}"/>
<mergeCells count="2"><mergeCell ref="A1:{last_column}1"/><mergeCell ref="A2:{last_column}2"/></mergeCells>
<pageMargins left="0.25" right="0.25" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>
<pageSetup orientation="landscape" fitToWidth="1" fitToHeight="0"/>
</worksheet>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="4"><font><sz val="11"/><name val="Segoe UI"/></font><font><b/><sz val="18"/><color rgb="FF101828"/><name val="Segoe UI"/></font><font><sz val="10"/><color rgb="FF667085"/><name val="Segoe UI"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Segoe UI"/></font></fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF2F6FED"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF4F7FB"/></patternFill></fill></fills>
<borders count="2"><border/><border><left style="thin"><color rgb="FFD0D5DD"/></left><right style="thin"><color rgb="FFD0D5DD"/></right><top style="thin"><color rgb="FFD0D5DD"/></top><bottom style="thin"><color rgb="FFD0D5DD"/></bottom></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="6"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/><xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/><xf numFmtId="0" fontId="3" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''
    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Hisobot" sheetId="1" r:id="rId1"/></sheets></workbook>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'''
    package_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>HR Control</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created></cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>HR Control</Application></Properties>'''
    files = {"[Content_Types].xml": content_types, "_rels/.rels": package_rels,
             "xl/workbook.xml": workbook, "xl/_rels/workbook.xml.rels": workbook_rels,
             "xl/worksheets/sheet1.xml": worksheet, "xl/styles.xml": styles,
             "docProps/core.xml": core, "docProps/app.xml": app}
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content.encode("utf-8"))
