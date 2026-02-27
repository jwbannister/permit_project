"""Excel writer: populate .xlsm template with source data.

Writes ONLY input columns (values), leaving all formula and array
formula columns untouched. The formulas recalculate when the workbook
is opened in Excel. The Python calculation engine provides an
independent verification path.
"""

import shutil
from pathlib import Path

import openpyxl

from eipop.excel.column_map import COLUMN_MAP, ColType
from eipop.models.source import SourceSpec
from eipop.models.emission_factors import EmissionFactors


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

        # Emission factors (input columns only — PM, CO, NOx are input; PM10, PM2.5, SO2, VOC are formulas)
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

    # Copy template to output location
    shutil.copy2(template_path, output_path)

    # Load the copy (preserving VBA)
    wb = openpyxl.load_workbook(output_path, keep_vba=True)
    ws = wb["Proc"]

    # Build the data for this row
    row_data = _build_row_data(source, factors)

    # Write only INPUT columns
    written = 0
    for col_letter, field_name, col_type in COLUMN_MAP:
        if col_type != ColType.INPUT:
            continue

        if field_name not in row_data:
            continue

        value = row_data[field_name]
        if value is None:
            continue

        col_idx = _col_letter_to_index(col_letter)
        ws.cell(row=row, column=col_idx, value=value)
        written += 1

    wb.save(output_path)
    wb.close()

    return output_path


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

    shutil.copy2(template_path, output_path)

    wb = openpyxl.load_workbook(output_path, keep_vba=True)
    ws = wb["Proc"]

    for row, source, factors in sources:
        row_data = _build_row_data(source, factors)

        for col_letter, field_name, col_type in COLUMN_MAP:
            if col_type != ColType.INPUT:
                continue
            if field_name not in row_data:
                continue
            value = row_data[field_name]
            if value is None:
                continue

            col_idx = _col_letter_to_index(col_letter)
            ws.cell(row=row, column=col_idx, value=value)

    wb.save(output_path)
    wb.close()

    return output_path
