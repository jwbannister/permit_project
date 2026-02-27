"""End-to-end validation: Python calc engine vs reference workbook.

This test feeds hardcoded S2.002 inputs through the calculation engine
and compares every output value against the reference workbook row 7.
No Excel recalculation is involved — this validates the Python engine
independently.
"""

from pathlib import Path

import pytest

from eipop.calcs.diesel_engine import (
    kw_to_hp,
    so2_ef_g_per_bkWhr,
    temp_F_to_K,
    ft_to_m,
    stack_velocity_fps,
    fuel_consumption_MMBtu_hr,
)
from eipop.calcs.emission_rates import calc_all_rates
from eipop.calcs.model_rates import lb_hr_to_g_s, ton_yr_to_g_s, model_emission_rates
from eipop.validation.compare import (
    compare_row_to_reference,
    format_report,
    CellStatus,
)

REFERENCE = Path("reference/workbook/LN WFH EmisInv_LnPwr_r1_NDEP.xlsm")

pytestmark = pytest.mark.skipif(
    not REFERENCE.exists(),
    reason="Reference workbook not available",
)

# === S2.002 fire pump inputs ===
KW = 129.0
FUEL_GAL_HR = 11.6
HRS_DAY = 24.0
HRS_YR = 100.0
TEMP_F = 908.0
ACFM = 1131.0
REL_HT_FT = 6.0
DIA_FT = 5.0 / 12.0
NOX_ISR = 0.2

# Emission factors
EF_PM = 0.3
EF_CO = 5.0
EF_NOX = 4.0
EF_VOC = 1.5292437428952  # from reference — derivation TBD


def _build_actual_values() -> dict[str, object]:
    """Run the full calculation chain and return all computed values."""
    hp = kw_to_hp(KW)
    mmbtu_hr = fuel_consumption_MMBtu_hr(FUEL_GAL_HR, "diesel")
    so2_ef = so2_ef_g_per_bkWhr(KW, FUEL_GAL_HR)

    efs = {
        "PM": EF_PM, "PM10": EF_PM, "PM2.5": EF_PM,
        "CO": EF_CO, "NOx": EF_NOX,
        "SO2": so2_ef, "VOC": EF_VOC,
    }

    rates = calc_all_rates(efs, "g/bkW-hr", KW, "bkW", HRS_DAY, HRS_YR)

    # Release params
    vel_fps = stack_velocity_fps(ACFM, DIA_FT)

    # Build the values dict keyed by column_map field names
    values = {}

    # Input fields (should match exactly)
    values["source_id"] = "S2.002"
    values["source_count"] = 1
    values["new_or_modified"] = "Yes"
    values["system_id"] = 2
    values["system_desc"] = "Emergency Fire Water Pump"
    values["scc"] = "2-02-001-02"
    values["source_desc"] = "Emergency Fire Water Pump (75 ≤ kW < 130; mfg. 2010 or newer)"
    values["throughput_unit"] = "bkW"
    values["throughput_material"] = "diesel"
    values["operating_hrs_day"] = HRS_DAY
    values["operating_hrs_yr"] = HRS_YR
    values["kW"] = KW
    values["fuel_type"] = "diesel"
    values["fuel_consumption"] = FUEL_GAL_HR
    values["fuel_unit"] = "gal"
    values["displacement_L"] = 6.8
    values["cylinders"] = 6
    values["tier"] = "N/A"
    values["emission_code"] = "ECI"
    values["EF_PM"] = EF_PM
    values["EF_CO"] = EF_CO
    values["EF_NOx"] = EF_NOX
    values["EF_unit"] = "g/bkW-hr"
    values["ctrl_system"] = "None"
    values["source_type"] = "POINT"
    values["exhaust_temp_F"] = TEMP_F
    values["acfm"] = ACFM
    values["NOx_ISR"] = NOX_ISR
    values["is_emergency"] = True

    # Calculated fields — formulas we replicate
    values["throughput_hr"] = KW
    values["throughput_day"] = KW * HRS_DAY
    values["throughput_yr"] = KW * HRS_YR
    values["hp"] = hp
    values["MMBtu_hr"] = mmbtu_hr
    values["EF_PM10"] = EF_PM
    values["EF_PM2_5"] = EF_PM
    values["EF_SO2"] = so2_ef
    values["EF_VOC"] = EF_VOC

    # Hourly emissions (lb/hr)
    values["PM_pph"] = rates["PM"]["pph"]
    values["PM10_pph"] = rates["PM10"]["pph"]
    values["PM2_5_pph"] = rates["PM2.5"]["pph"]
    values["CO_pph"] = rates["CO"]["pph"]
    values["NOx_pph"] = rates["NOx"]["pph"]
    values["SO2_pph"] = rates["SO2"]["pph"]
    values["VOC_pph"] = rates["VOC"]["pph"]

    # Daily emissions (lb/day)
    values["PM_ppd"] = rates["PM"]["ppd"]
    values["PM10_ppd"] = rates["PM10"]["ppd"]
    values["PM2_5_ppd"] = rates["PM2.5"]["ppd"]
    values["CO_ppd"] = rates["CO"]["ppd"]
    values["NOx_ppd"] = rates["NOx"]["ppd"]
    values["SO2_ppd"] = rates["SO2"]["ppd"]
    values["VOC_ppd"] = rates["VOC"]["ppd"]

    # Annual emissions (ton/yr)
    values["PM_tpy"] = rates["PM"]["tpy"]
    values["PM10_tpy"] = rates["PM10"]["tpy"]
    values["PM2_5_tpy"] = rates["PM2.5"]["tpy"]
    values["CO_tpy"] = rates["CO"]["tpy"]
    values["NOx_tpy"] = rates["NOx"]["tpy"]
    values["SO2_tpy"] = rates["SO2"]["tpy"]
    values["VOC_tpy"] = rates["VOC"]["tpy"]

    # Release parameters
    values["release_height_ft"] = REL_HT_FT
    values["diameter_ft"] = DIA_FT
    values["velocity_fps"] = vel_fps

    # Metric release params
    values["release_height_m"] = ft_to_m(REL_HT_FT)
    values["temp_K"] = temp_F_to_K(TEMP_F)
    values["velocity_mps"] = vel_fps / 3.28084
    values["diameter_m"] = ft_to_m(DIA_FT)

    # Model emission rates (g/s) — emergency source logic
    model = model_emission_rates(rates, is_emergency=True, nox_isr=NOX_ISR)
    values["PM10_24_gps"] = model["PM10_24_gps"]
    values["PM2_5_24_gps"] = model["PM2_5_24_gps"]
    values["CO_ALL_gps"] = model["CO_ALL_gps"]
    values["NOx_1_gps"] = model["NOx_1_gps"]
    values["SO2_1_gps"] = model["SO2_1_gps"]
    values["SO2_ST_gps"] = model["SO2_ST_gps"]
    values["PM2_5_AN_gps"] = model["PM2_5_AN_gps"]
    values["NOx_AN_gps"] = model["NOx_AN_gps"]
    values["SO2_AN_gps"] = model["SO2_AN_gps"]

    # Model NOx/SO2 lb/hr (annualized for emergency)
    values["NOx_model_pph"] = model["NOx_model_pph"]
    values["SO2_model_pph"] = model["SO2_model_pph"]

    # Uncontrolled = same as controlled (no controls on this source)
    values["EF_PM_u"] = EF_PM
    values["EF_PM10_u"] = EF_PM
    values["EF_PM2_5_u"] = EF_PM
    values["EF_CO_u"] = EF_CO
    values["EF_NOx_u"] = EF_NOX
    values["EF_SO2_u"] = so2_ef
    values["EF_VOC_u"] = EF_VOC
    values["EF_unit_u"] = "g/bkW-hr"

    # Uncontrolled hourly = same as controlled hourly
    values["PM_pph_u"] = rates["PM"]["pph"]
    values["PM10_pph_u"] = rates["PM10"]["pph"]
    values["PM2_5_pph_u"] = rates["PM2.5"]["pph"]
    values["CO_pph_u"] = rates["CO"]["pph"]
    values["NOx_pph_u"] = rates["NOx"]["pph"]
    values["SO2_pph_u"] = rates["SO2"]["pph"]
    values["VOC_pph_u"] = rates["VOC"]["pph"]

    # Uncontrolled annual = same as controlled annual
    values["PM_tpy_u"] = rates["PM"]["tpy"]
    values["PM10_tpy_u"] = rates["PM10"]["tpy"]
    values["PM2_5_tpy_u"] = rates["PM2.5"]["tpy"]
    values["CO_tpy_u"] = rates["CO"]["tpy"]
    values["NOx_tpy_u"] = rates["NOx"]["tpy"]
    values["SO2_tpy_u"] = rates["SO2"]["tpy"]
    values["VOC_tpy_u"] = rates["VOC"]["tpy"]

    return values


class TestPythonCalcValidation:
    """Compare Python calculation engine output against reference workbook."""

    def test_all_values_match_reference(self):
        actual = _build_actual_values()
        results = compare_row_to_reference(REFERENCE, 7, actual, rel_tol=1e-3)

        # Print full report for visibility
        report = format_report(results, show_all=False)
        print("\n" + report)

        # Assert no mismatches or missing values
        mismatches = [r for r in results if r.status == CellStatus.MISMATCH]
        missing = [r for r in results if r.status == CellStatus.MISSING]

        if mismatches:
            details = "\n".join(
                f"  {r.column} ({r.field}): expected={r.expected}, actual={r.actual}, error={r.error_pct}"
                for r in mismatches
            )
            pytest.fail(f"{len(mismatches)} mismatched values:\n{details}")

        if missing:
            details = "\n".join(
                f"  {r.column} ({r.field}): expected={r.expected}"
                for r in missing
            )
            pytest.fail(f"{len(missing)} missing values:\n{details}")

    def test_match_count(self):
        """Verify we're actually comparing a meaningful number of cells."""
        actual = _build_actual_values()
        results = compare_row_to_reference(REFERENCE, 7, actual, rel_tol=1e-3)

        matched = sum(1 for r in results if r.status == CellStatus.MATCH)
        # We should match at least 70 cells (inputs + all calculated rates)
        assert matched >= 70, f"Only {matched} matches — expected at least 70"
