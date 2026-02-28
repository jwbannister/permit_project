"""Excel writer: populate .xlsm template with source data.

Uses direct zip/XML manipulation to modify ONLY the Proc sheet XML,
leaving all other files (VBA, charts, drawings, styles, etc.)
byte-for-byte identical to the template. This avoids the repair
dialog that openpyxl's keep_vba=True mode triggers.

Writes ONLY input columns (values), leaving all formula and array
formula columns untouched.
"""

import shutil
import zipfile
from io import BytesIO
from pathlib import Path

import openpyxl

from eipop.excel.column_map import COLUMN_MAP, ColType
from eipop.models.source import SourceSpec
from eipop.models.emission_factors import EmissionFactors


# The Proc sheet is sheet3.xml in the template zip
_PROC_SHEET_PATH = "xl/worksheets/sheet3.xml"


# Mapping from SourceSpec/EmissionFactors fields to column_map field names.
# Only INPUT columns — formula columns are never written.
def _build_row_data(source: SourceSpec, factors: EmissionFactors) -> dict[str, object]:
    """Build a dict of {column_map_field: value} for all INPUT columns."""
    return {
        # Source identification
        "source_id": source.source_id,
        "source_count": source.source_count,
        "new_or_modified": source.new_or_modified,
        "system_id": source.system_id,
        "system_desc": source.system_desc,
        "scc": source.scc,
        "source_desc": source.source_desc,

        # Throughput
        "throughput_unit": source.throughput_unit,
        "throughput_material": source.fuel_type,
        "operating_hrs_day": source.operating_hrs_day,
        "operating_hrs_yr": source.operating_hrs_yr,

        # Equipment specs
        "kW": source.kW,
        "fuel_type": source.fuel_type,
        "fuel_consumption": source.fuel_consumption,
        "fuel_unit": source.fuel_unit,
        "displacement_L": source.displacement_L,
        "cylinders": source.cylinders,
        "tier": source.tier,
        "emission_code": source.emission_code,
        "spec_reference": source.spec_reference,

        # Emission factors
        "EF_PM": factors.PM.value,
        "EF_CO": factors.CO.value,
        "EF_NOx": factors.NOx.value,
        "EF_unit": factors.ef_unit,
        "EF_reference": factors.reference,
        "ctrl_system": "None",

        # Release parameters
        "source_type": source.source_type,
        "exhaust_temp_F": source.exhaust_temp_F,
        "acfm": source.exhaust_flow_acfm,
        "release_reference": source.equipment_reference,

        # Location
        "location_reference": source.location_reference,

        # Regulatory
        "cfr_reference": source.cfr_reference,
        "state_regulation": source.state_regulation,

        # NOx ISR
        "NOx_ISR": source.nox_isr,

        # Emergency
        "is_emergency": source.is_emergency,
    }


def _col_letter_to_index(col_letter: str) -> int:
    """Convert column letter(s) to 1-based column index."""
    return openpyxl.utils.column_index_from_string(col_letter)


def _write_rows_to_sheet_xml(
    sheet_xml_bytes: bytes,
    rows: list[tuple[int, dict[str, object]]],
) -> bytes:
    """Modify the Proc sheet XML to insert cell values.

    Loads just the sheet XML with openpyxl's worksheet parser,
    writes the values, and returns the modified XML bytes.
    This is done in-memory without touching the full workbook.
    """
    # We use openpyxl to parse/modify just the single sheet XML.
    # To do this, we create a minimal workbook in memory, load the
    # sheet XML into it, write our values, then extract the XML.
    # Unfortunately openpyxl doesn't support single-sheet loading,
    # so we use a different approach: parse the XML with lxml/ET
    # and inject cell values directly.
    import xml.etree.ElementTree as ET

    # Parse the sheet XML
    # Register namespace prefixes to preserve them on output
    namespaces = {
        '': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
        'x14ac': 'http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac',
        'xr': 'http://schemas.microsoft.com/office/spreadsheetml/2014/revision',
        'xr6': 'http://schemas.microsoft.com/office/spreadsheetml/2014/revision6',
        'xr10': 'http://schemas.microsoft.com/office/spreadsheetml/2014/revision10',
        'xr2': 'http://schemas.microsoft.com/office/spreadsheetml/2015/revision2',
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    tree = ET.ElementTree(ET.fromstring(sheet_xml_bytes))
    root = tree.getroot()

    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    ns_prefix = f'{{{ns}}}'

    # Build a map of column_letter -> field_name for INPUT columns only
    input_cols = {}
    for col_letter, field_name, col_type in COLUMN_MAP:
        if col_type == ColType.INPUT:
            input_cols[col_letter] = field_name

    # Find the sheetData element
    sheet_data = root.find(f'{ns_prefix}sheetData')
    if sheet_data is None:
        raise ValueError("No sheetData element found in sheet XML")

    # Build a map of existing rows by row number
    row_elements = {}
    for row_elem in sheet_data.findall(f'{ns_prefix}row'):
        row_num = int(row_elem.get('r'))
        row_elements[row_num] = row_elem

    for row_num, row_data in rows:
        row_elem = row_elements.get(row_num)
        if row_elem is None:
            # Create a new row element
            row_elem = ET.SubElement(sheet_data, f'{ns_prefix}row')
            row_elem.set('r', str(row_num))
            row_elements[row_num] = row_elem

        # Build a map of existing cells in this row by column
        existing_cells = {}
        for cell_elem in row_elem.findall(f'{ns_prefix}c'):
            cell_ref = cell_elem.get('r')
            existing_cells[cell_ref] = cell_elem

        for col_letter, field_name in input_cols.items():
            if field_name not in row_data:
                continue
            value = row_data[field_name]
            if value is None:
                continue

            cell_ref = f"{col_letter}{row_num}"
            cell_elem = existing_cells.get(cell_ref)

            if cell_elem is None:
                # Create new cell element
                cell_elem = ET.SubElement(row_elem, f'{ns_prefix}c')
                cell_elem.set('r', cell_ref)

            # Remove any existing value or formula
            for child_tag in (f'{ns_prefix}v', f'{ns_prefix}f'):
                existing = cell_elem.find(child_tag)
                if existing is not None:
                    cell_elem.remove(existing)

            # Set the value
            if isinstance(value, bool):
                cell_elem.set('t', 'b')
                v_elem = ET.SubElement(cell_elem, f'{ns_prefix}v')
                v_elem.text = '1' if value else '0'
            elif isinstance(value, (int, float)):
                # Remove any string type indicator
                if 't' in cell_elem.attrib:
                    del cell_elem.attrib['t']
                v_elem = ET.SubElement(cell_elem, f'{ns_prefix}v')
                v_elem.text = str(value)
            elif isinstance(value, str):
                cell_elem.set('t', 'inlineStr')
                is_elem = ET.SubElement(cell_elem, f'{ns_prefix}is')
                t_elem = ET.SubElement(is_elem, f'{ns_prefix}t')
                t_elem.text = value
            else:
                # Fallback: convert to string
                cell_elem.set('t', 'inlineStr')
                is_elem = ET.SubElement(cell_elem, f'{ns_prefix}is')
                t_elem = ET.SubElement(is_elem, f'{ns_prefix}t')
                t_elem.text = str(value)

    # Serialize back to bytes
    return ET.tostring(root, xml_declaration=True, encoding='UTF-8')


def _write_to_zip(
    template_path: Path,
    output_path: Path,
    rows: list[tuple[int, dict[str, object]]],
) -> Path:
    """Copy template and replace only the Proc sheet XML."""
    # Read the original sheet XML
    with zipfile.ZipFile(template_path, 'r') as zin:
        original_sheet = zin.read(_PROC_SHEET_PATH)

    # Modify just the sheet XML
    modified_sheet = _write_rows_to_sheet_xml(original_sheet, rows)

    # Build output zip: copy everything from template, replace sheet3.xml
    with zipfile.ZipFile(template_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == _PROC_SHEET_PATH:
                    zout.writestr(item, modified_sheet)
                else:
                    zout.writestr(item, zin.read(item.filename))

    return output_path


def populate_template(
    template_path: str | Path,
    output_path: str | Path,
    row: int,
    source: SourceSpec,
    factors: EmissionFactors,
) -> Path:
    """Populate a single row in the template workbook.

    Args:
        template_path: Path to the template .xlsm file
        output_path: Path for the populated output .xlsm file
        row: Row number in the Proc sheet (6-25)
        source: Source specification data
        factors: Emission factors for this source

    Returns:
        Path to the populated workbook
    """
    template_path = Path(template_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    row_data = _build_row_data(source, factors)
    return _write_to_zip(template_path, output_path, [(row, row_data)])


def populate_multiple(
    template_path: str | Path,
    output_path: str | Path,
    sources: list[tuple[int, SourceSpec, EmissionFactors]],
) -> Path:
    """Populate multiple rows in the template workbook.

    Args:
        template_path: Path to the template .xlsm file
        output_path: Path for the populated output .xlsm file
        sources: List of (row_number, source, factors) tuples

    Returns:
        Path to the populated workbook
    """
    template_path = Path(template_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [(row, _build_row_data(source, factors)) for row, source, factors in sources]
    return _write_to_zip(template_path, output_path, rows)


def populate_raw(
    template_path: str | Path,
    output_path: str | Path,
    rows: list[tuple[int, dict[str, object]]],
) -> Path:
    """Populate multiple rows using raw data dicts.

    Args:
        template_path: Path to the template .xlsm file
        output_path: Path for the populated output .xlsm file
        rows: List of (row_number, field_data_dict) tuples

    Returns:
        Path to the populated workbook
    """
    template_path = Path(template_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return _write_to_zip(template_path, output_path, rows)
