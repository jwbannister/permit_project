#!/usr/bin/env python3
"""End-to-end EI-POP pipeline for the S2.002 fire pump.

Demonstrates the full flow:
  1. Parse spec sheet PDF → equipment specs
  2. Select emission factors using regulatory hierarchy
  3. Calculate all emission rates
  4. Populate Excel workbook template
  5. (Development only) Validate against reference workbook

Usage:
    python scripts/run_fire_pump.py

Inputs:
    - reference/client_docs/Sys2_example_Fire_Pump_ju6h-ufabl0-usa.pdf
    - templates/LN_WFH_EmisInv_template.xlsm

Outputs:
    - output/LN_WFH_EmisInv_populated.xlsm (production output)
    - stdout validation report (development output)
"""

from pathlib import Path

from eipop.parsers.spec_sheet import parse_spec_sheet, get_rated_speed_data
from eipop.calcs.ef_selection import select_emission_factors
from eipop.calcs.diesel_engine import so2_ef_g_per_bkWhr
from eipop.calcs.emission_rates import calc_all_rates
from eipop.calcs.model_rates import model_emission_rates, model_release_params
from eipop.models.source import SourceSpec
from eipop.models.emission_factors import EmissionFactors
from eipop.excel.writer import populate_template


# ── Paths ──
SPEC_PDF = Path("reference/client_docs/Sys2_example_Fire_Pump_ju6h-ufabl0-usa.pdf")
TEMPLATE = Path("templates/LN_WFH_EmisInv_template.xlsm")
OUTPUT = Path("output/LN_WFH_EmisInv_populated.xlsm")
REFERENCE = Path("reference/workbook/LN WFH EmisInv_LnPwr_r1_NDEP.xlsm")

# ── Fixed inputs (from project scope / client data) ──
# These would come from a project config or user input in production
OPERATING_HRS_DAY = 24.0
OPERATING_HRS_YR = 100.0
IS_EMERGENCY = True
RELEASE_HEIGHT_FT = 6.0
STACK_DIAMETER_FT = 5.0 / 12.0
NOX_ISR = 0.2
RATED_RPM = 2350


def main():
    # ── Step 1: Parse spec sheet ──
    print("Step 1: Parsing spec sheet...")
    spec = parse_spec_sheet(SPEC_PDF)
    rated = get_rated_speed_data(spec, rated_rpm=RATED_RPM)

    kW = rated["kw"]
    fuel_gph = rated["fuel_consumption_gph"]
    print(f"  Model: {spec.model}")
    print(f"  Engine: {spec.engine_series}")
    print(f"  Power: {rated['bhp']} BHP / {kW} kW")
    print(f"  Fuel: {fuel_gph} gal/hr")
    print(f"  Exhaust: {rated['exhaust_temp_F']}°F, {rated['exhaust_flow_cfm']} ACFM")
    print(f"  Pipe Dia: {rated['exhaust_pipe_dia_in']}\"")
    print()

    # ── Step 2: Select emission factors ──
    print("Step 2: Selecting emission factors...")
    efs = select_emission_factors(
        kW=kW,
        fuel_type="diesel",
        fuel_consumption_gal_hr=fuel_gph,
        is_fire_pump=True,
    )
    print(f"  PM/PM10/PM2.5: {efs.PM.value} g/bkW-hr ({efs.PM.source})")
    print(f"  CO: {efs.CO.value} g/bkW-hr")
    print(f"  NOx: {efs.NOx.value} g/bkW-hr")
    print(f"  SO2: {efs.SO2.value:.6f} g/bkW-hr ({efs.SO2.source})")
    print(f"  VOC: {efs.VOC.value:.4f} g/bkW-hr ({efs.VOC.source})")
    print()

    # ── Step 3: Calculate emission rates ──
    print("Step 3: Calculating emission rates...")
    ef_dict = {
        "PM": efs.PM.value, "PM10": efs.PM10.value, "PM2.5": efs.PM2_5.value,
        "CO": efs.CO.value, "NOx": efs.NOx.value,
        "SO2": efs.SO2.value, "VOC": efs.VOC.value,
    }
    rates = calc_all_rates(
        ef_dict, efs.ef_unit, kW, "bkW",
        OPERATING_HRS_DAY, OPERATING_HRS_YR,
    )
    print(f"  NOx: {rates['NOx']['pph']:.4f} lb/hr, {rates['NOx']['tpy']:.6f} ton/yr")
    print(f"  CO:  {rates['CO']['pph']:.4f} lb/hr, {rates['CO']['tpy']:.6f} ton/yr")
    print(f"  PM:  {rates['PM']['pph']:.4f} lb/hr, {rates['PM']['tpy']:.6f} ton/yr")
    print()

    # ── Step 4: Build SourceSpec and populate workbook ──
    print("Step 4: Populating Excel workbook...")
    source = SourceSpec(
        source_id="S2.002",
        source_count=1,
        new_or_modified="Yes",
        system_id=2,
        system_desc="Emergency Fire Water Pump",
        scc="2-02-001-02",
        source_desc="Emergency Fire Water Pump (75 ≤ kW < 130; mfg. 2010 or newer)",
        kW=kW,
        fuel_type="diesel",
        fuel_consumption=fuel_gph,
        fuel_unit="gal",
        displacement_L=rated["displacement_L"],
        cylinders=rated["cylinders"],
        tier="N/A",
        operating_hrs_day=OPERATING_HRS_DAY,
        operating_hrs_yr=OPERATING_HRS_YR,
        is_emergency=IS_EMERGENCY,
        throughput_unit="bkW",
        source_type="POINT",
        exhaust_temp_F=rated["exhaust_temp_F"],
        exhaust_flow_acfm=rated["exhaust_flow_cfm"],
        emission_code="ECI",
        nox_isr=NOX_ISR,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    populate_template(TEMPLATE, OUTPUT, row=7, source=source, factors=efs)
    print(f"  Output: {OUTPUT}")
    print()

    # ── Step 5 (Development): Validate against reference ──
    if REFERENCE.exists():
        print("Step 5: Validating against reference workbook...")
        _run_validation(kW, fuel_gph, efs, rates, rated, source)
    else:
        print("Step 5: Skipped (no reference workbook)")


def _run_validation(kW, fuel_gph, efs, rates, rated, source):
    """Development-only: compare calculated values against reference."""
    from eipop.calcs.diesel_engine import (
        kw_to_hp, fuel_consumption_MMBtu_hr,
        temp_F_to_K, ft_to_m, stack_velocity_fps,
    )
    from eipop.validation.compare import (
        compare_row_to_reference, format_report, CellStatus,
    )

    hp = kw_to_hp(kW)
    mmbtu_hr = fuel_consumption_MMBtu_hr(fuel_gph, "diesel")
    vel_fps = stack_velocity_fps(rated["exhaust_flow_cfm"], STACK_DIAMETER_FT)
    model = model_emission_rates(rates, is_emergency=IS_EMERGENCY, nox_isr=NOX_ISR)

    # Build the full values dict for comparison
    values = {}

    # Inputs
    values["source_id"] = source.source_id
    values["source_count"] = source.source_count
    values["new_or_modified"] = source.new_or_modified
    values["system_id"] = source.system_id
    values["system_desc"] = source.system_desc
    values["scc"] = source.scc
    values["source_desc"] = source.source_desc
    values["throughput_unit"] = source.throughput_unit
    values["throughput_material"] = source.fuel_type
    values["operating_hrs_day"] = OPERATING_HRS_DAY
    values["operating_hrs_yr"] = OPERATING_HRS_YR
    values["kW"] = kW
    values["fuel_type"] = source.fuel_type
    values["fuel_consumption"] = fuel_gph
    values["fuel_unit"] = source.fuel_unit
    values["displacement_L"] = rated["displacement_L"]
    values["cylinders"] = rated["cylinders"]
    values["tier"] = source.tier
    values["emission_code"] = source.emission_code
    values["EF_PM"] = efs.PM.value
    values["EF_CO"] = efs.CO.value
    values["EF_NOx"] = efs.NOx.value
    values["EF_unit"] = efs.ef_unit
    values["ctrl_system"] = "None"
    values["source_type"] = source.source_type
    values["exhaust_temp_F"] = rated["exhaust_temp_F"]
    values["acfm"] = rated["exhaust_flow_cfm"]
    values["NOx_ISR"] = NOX_ISR
    values["is_emergency"] = IS_EMERGENCY

    # Calculated
    values["throughput_hr"] = kW
    values["throughput_day"] = kW * OPERATING_HRS_DAY
    values["throughput_yr"] = kW * OPERATING_HRS_YR
    values["hp"] = hp
    values["MMBtu_hr"] = mmbtu_hr
    values["EF_PM10"] = efs.PM10.value
    values["EF_PM2_5"] = efs.PM2_5.value
    values["EF_SO2"] = efs.SO2.value
    values["EF_VOC"] = efs.VOC.value

    # Emission rates
    for pol in ["PM", "PM10", "CO", "NOx", "SO2", "VOC"]:
        p = pol if pol != "PM10" else "PM10"
        values[f"{pol}_pph"] = rates[p]["pph"]
        values[f"{pol}_ppd"] = rates[p]["ppd"]
        values[f"{pol}_tpy"] = rates[p]["tpy"]
    values["PM2_5_pph"] = rates["PM2.5"]["pph"]
    values["PM2_5_ppd"] = rates["PM2.5"]["ppd"]
    values["PM2_5_tpy"] = rates["PM2.5"]["tpy"]

    # Release params
    values["release_height_ft"] = RELEASE_HEIGHT_FT
    values["diameter_ft"] = STACK_DIAMETER_FT
    values["velocity_fps"] = vel_fps
    values["release_height_m"] = ft_to_m(RELEASE_HEIGHT_FT)
    values["temp_K"] = temp_F_to_K(rated["exhaust_temp_F"])
    values["velocity_mps"] = vel_fps / 3.28084
    values["diameter_m"] = ft_to_m(STACK_DIAMETER_FT)

    # Model rates
    values["PM10_24_gps"] = model["PM10_24_gps"]
    values["PM2_5_24_gps"] = model["PM2_5_24_gps"]
    values["CO_ALL_gps"] = model["CO_ALL_gps"]
    values["NOx_1_gps"] = model["NOx_1_gps"]
    values["SO2_1_gps"] = model["SO2_1_gps"]
    values["SO2_ST_gps"] = model["SO2_ST_gps"]
    values["PM2_5_AN_gps"] = model["PM2_5_AN_gps"]
    values["NOx_AN_gps"] = model["NOx_AN_gps"]
    values["SO2_AN_gps"] = model["SO2_AN_gps"]
    values["NOx_model_pph"] = model["NOx_model_pph"]
    values["SO2_model_pph"] = model["SO2_model_pph"]

    # Uncontrolled = controlled (no controls)
    values["EF_PM_u"] = efs.PM.value
    values["EF_PM10_u"] = efs.PM10.value
    values["EF_PM2_5_u"] = efs.PM2_5.value
    values["EF_CO_u"] = efs.CO.value
    values["EF_NOx_u"] = efs.NOx.value
    values["EF_SO2_u"] = efs.SO2.value
    values["EF_VOC_u"] = efs.VOC.value
    values["EF_unit_u"] = efs.ef_unit
    for pol in ["PM", "PM10", "CO", "NOx", "SO2", "VOC"]:
        values[f"{pol}_pph_u"] = rates[pol]["pph"]
        values[f"{pol}_tpy_u"] = rates[pol]["tpy"]
    values["PM2_5_pph_u"] = rates["PM2.5"]["pph"]
    values["PM2_5_tpy_u"] = rates["PM2.5"]["tpy"]

    results = compare_row_to_reference(REFERENCE, 7, values, rel_tol=1e-3)
    report = format_report(results, show_all=False)
    print(report)

    matched = sum(1 for r in results if r.status == CellStatus.MATCH)
    mismatched = sum(1 for r in results if r.status == CellStatus.MISMATCH)
    print(f"\n  Result: {matched} matched, {mismatched} mismatched")


if __name__ == "__main__":
    main()
