"""Bidirectional mapping between Proc sheet columns and field names.

Columns are categorized as INPUT (values we write) or CALC (formulas
we leave untouched). The Excel writer only populates INPUT columns.

Column letters and header names are from the reference workbook
(LN WFH EmisInv_LnPwr_r1_NDEP.xlsm), Proc sheet row 1.
"""

from enum import Enum


class ColType(Enum):
    INPUT = "input"  # Value cells — we write these
    FORMULA = "formula"  # Formula cells — leave untouched
    ARRAY = "array"  # Array formula cells — leave untouched


# (column_letter, field_name, col_type)
# Ordered by column position in the Proc sheet
COLUMN_MAP: list[tuple[str, str, ColType]] = [
    # --- Source identification ---
    ("A", "source_id", ColType.INPUT),
    ("B", "model_id", ColType.FORMULA),  # =SUBSTITUTE(A,".",""
    ("C", "source_count", ColType.INPUT),
    ("D", "new_or_modified", ColType.INPUT),
    ("E", "system_id", ColType.INPUT),
    ("F", "system_desc", ColType.INPUT),
    ("G", "scc", ColType.INPUT),
    ("H", "source_desc", ColType.INPUT),

    # --- Throughput / operating limits ---
    ("I", "throughput_hr", ColType.FORMULA),  # =S (kW)
    ("J", "throughput_day", ColType.FORMULA),  # =I*N
    ("K", "throughput_yr", ColType.FORMULA),  # =I*O
    ("L", "throughput_unit", ColType.INPUT),
    ("M", "throughput_material", ColType.INPUT),
    ("N", "operating_hrs_day", ColType.INPUT),
    ("O", "operating_hrs_yr", ColType.INPUT),
    # P: "other" — rarely used
    ("Q", "equipment_data_ref", ColType.FORMULA),  # =References!$A$19

    # --- Combustion equipment specs (info only, not used in calcs) ---
    ("R", "hp", ColType.FORMULA),  # =S*$I$34
    ("S", "kW", ColType.INPUT),
    ("T", "fuel_type", ColType.INPUT),
    ("U", "fuel_consumption", ColType.INPUT),
    ("V", "fuel_unit", ColType.INPUT),
    ("W", "MMBtu_hr", ColType.ARRAY),  # array formula
    ("X", "displacement_L", ColType.INPUT),
    ("Y", "cylinders", ColType.INPUT),
    ("Z", "tier", ColType.INPUT),
    ("AA", "emission_code", ColType.INPUT),
    ("AB", "spec_reference", ColType.INPUT),

    # --- Emission factors ---
    ("AC", "EF_PM", ColType.INPUT),
    ("AD", "EF_PM10", ColType.FORMULA),  # =AC (same as PM for diesel)
    ("AE", "EF_PM2_5", ColType.FORMULA),  # =AC (same as PM for diesel)
    ("AF", "EF_CO", ColType.INPUT),
    ("AG", "EF_NOx", ColType.INPUT),
    ("AH", "EF_SO2", ColType.FORMULA),  # mass balance formula
    ("AI", "EF_VOC", ColType.FORMULA),  # AP-42 formula
    ("AJ", "EF_unit", ColType.INPUT),
    ("AK", "EF_reference", ColType.INPUT),
    ("AL", "ctrl_system", ColType.INPUT),
    ("AM", "ctrl_eff", ColType.INPUT),  # typically empty (no control)

    # --- Hourly emissions (lb/hr) — all formulas ---
    ("AO", "PM_pph", ColType.ARRAY),
    ("AP", "PM10_pph", ColType.ARRAY),
    ("AQ", "PM2_5_pph", ColType.ARRAY),
    ("AR", "CO_pph", ColType.ARRAY),
    ("AS", "NOx_pph", ColType.ARRAY),
    ("AT", "SO2_pph", ColType.ARRAY),
    ("AU", "VOC_pph", ColType.ARRAY),

    # --- Daily emissions (lb/day) — all formulas ---
    ("AV", "PM_ppd", ColType.ARRAY),
    ("AW", "PM10_ppd", ColType.ARRAY),
    ("AX", "PM2_5_ppd", ColType.ARRAY),
    ("AY", "CO_ppd", ColType.ARRAY),
    ("AZ", "NOx_ppd", ColType.ARRAY),
    ("BA", "SO2_ppd", ColType.ARRAY),
    ("BB", "VOC_ppd", ColType.ARRAY),

    # --- Annual emissions (ton/yr) — all formulas ---
    ("BC", "PM_tpy", ColType.ARRAY),
    ("BD", "PM10_tpy", ColType.ARRAY),
    ("BE", "PM2_5_tpy", ColType.ARRAY),
    ("BF", "CO_tpy", ColType.ARRAY),
    ("BG", "NOx_tpy", ColType.ARRAY),
    ("BH", "SO2_tpy", ColType.ARRAY),
    ("BI", "VOC_tpy", ColType.ARRAY),

    # --- Location ---
    ("BJ", "UTM_easting", ColType.FORMULA),
    ("BK", "UTM_northing", ColType.FORMULA),
    ("BL", "location_reference", ColType.INPUT),
    ("BM", "elevation_m", ColType.FORMULA),
    ("BN", "elevation_reference", ColType.INPUT),  # actually formula in some rows

    # --- Release parameters (input) ---
    ("BO", "source_type", ColType.INPUT),
    ("BP", "release_height_ft", ColType.FORMULA),
    ("BQ", "exhaust_temp_F", ColType.INPUT),
    ("BR", "dscfm", ColType.FORMULA),
    ("BS", "acfm", ColType.INPUT),
    ("BT", "velocity_fps", ColType.FORMULA),
    ("BU", "diameter_ft", ColType.FORMULA),
    ("BV", "release_reference", ColType.INPUT),

    # --- Regulatory applicability ---
    ("BW", "cfr_reference", ColType.INPUT),
    ("BX", "state_regulation", ColType.INPUT),
    # BY: insignificant — rarely used

    # --- Model emission rates (g/s) and release params (metric) — all formulas ---
    ("BZ", "PM10_24_gps", ColType.FORMULA),
    ("CA", "PM2_5_24_gps", ColType.FORMULA),
    ("CB", "CO_ALL_gps", ColType.FORMULA),
    ("CC", "NOx_1_gps", ColType.FORMULA),
    ("CD", "SO2_1_gps", ColType.FORMULA),
    ("CE", "SO2_ST_gps", ColType.FORMULA),
    ("CF", "PM2_5_AN_gps", ColType.FORMULA),
    ("CG", "NOx_AN_gps", ColType.FORMULA),
    ("CH", "SO2_AN_gps", ColType.FORMULA),
    ("CI", "release_height_m", ColType.FORMULA),
    ("CJ", "temp_K", ColType.FORMULA),
    ("CK", "velocity_mps", ColType.FORMULA),
    ("CL", "diameter_m", ColType.FORMULA),

    # --- NOx ISR ---
    ("CM", "NOx_ISR", ColType.INPUT),
    ("CN", "ISR_reference", ColType.FORMULA),

    # --- Model NOx/SO2 (lb/hr with ISR applied) ---
    ("CO", "NOx_model_pph", ColType.FORMULA),
    ("CP", "SO2_model_pph", ColType.FORMULA),

    # --- Emergency flag ---
    ("CQ", "is_emergency", ColType.INPUT),

    # --- Uncontrolled emission factors (repeat of AC-AK for regulatory) ---
    ("CR", "EF_PM_u", ColType.FORMULA),
    ("CS", "EF_PM10_u", ColType.FORMULA),
    ("CT", "EF_PM2_5_u", ColType.FORMULA),
    ("CU", "EF_CO_u", ColType.FORMULA),
    ("CV", "EF_NOx_u", ColType.FORMULA),
    ("CW", "EF_SO2_u", ColType.FORMULA),
    ("CX", "EF_VOC_u", ColType.FORMULA),
    ("CY", "EF_unit_u", ColType.FORMULA),
    ("CZ", "EF_reference_u", ColType.FORMULA),

    # --- Uncontrolled hourly emissions (lb/hr) ---
    ("DA", "PM_pph_u", ColType.ARRAY),
    ("DB", "PM10_pph_u", ColType.ARRAY),
    ("DC", "PM2_5_pph_u", ColType.ARRAY),
    ("DD", "CO_pph_u", ColType.ARRAY),
    ("DE", "NOx_pph_u", ColType.ARRAY),
    ("DF", "SO2_pph_u", ColType.ARRAY),
    ("DG", "VOC_pph_u", ColType.ARRAY),

    # --- Uncontrolled annual emissions (ton/yr) ---
    ("DH", "PM_tpy_u", ColType.ARRAY),
    ("DI", "PM10_tpy_u", ColType.ARRAY),
    ("DJ", "PM2_5_tpy_u", ColType.ARRAY),
    ("DK", "CO_tpy_u", ColType.ARRAY),
    ("DL", "NOx_tpy_u", ColType.ARRAY),
    ("DM", "SO2_tpy_u", ColType.ARRAY),
    ("DN", "VOC_tpy_u", ColType.ARRAY),
]

# Lookup helpers
_by_field: dict[str, tuple[str, ColType]] = {
    field: (col, ctype) for col, field, ctype in COLUMN_MAP
}
_by_col: dict[str, tuple[str, ColType]] = {
    col: (field, ctype) for col, field, ctype in COLUMN_MAP
}


def col_for_field(field_name: str) -> str:
    """Return the Excel column letter for a field name."""
    return _by_field[field_name][0]


def field_for_col(col_letter: str) -> str:
    """Return the field name for an Excel column letter."""
    return _by_col[col_letter][0]


def input_columns() -> list[tuple[str, str]]:
    """Return (column_letter, field_name) for all INPUT columns."""
    return [(col, field) for col, field, ctype in COLUMN_MAP if ctype == ColType.INPUT]


def formula_columns() -> list[tuple[str, str]]:
    """Return (column_letter, field_name) for all FORMULA/ARRAY columns."""
    return [
        (col, field)
        for col, field, ctype in COLUMN_MAP
        if ctype in (ColType.FORMULA, ColType.ARRAY)
    ]
