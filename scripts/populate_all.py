#!/usr/bin/env python3
"""Populate the emissions inventory workbook with all 20 source rows.

Writes INPUT columns only — all formula/array columns recalculate
when the workbook is opened in Excel.

Sources:
  Row 6:     S2.001    Emergency Generator (560 kW diesel)
  Row 7:     S2.002    Emergency Fire Water Pump (129 kW diesel)
  Rows 8-24: IA1.xxx   Propane combustion sources (17 rows)
  Row 25:    IA1.109   Diesel storage tank

Usage:
    python scripts/populate_all.py
"""

from pathlib import Path

from eipop.excel.writer import populate_raw

TEMPLATE = Path("templates/LN_WFH_EmisInv_template.xlsm")
OUTPUT = Path("output/LN_WFH_EmisInv_populated.xlsm")

# ──────────────────────────────────────────────────────────────
# Row 6: S2.001 Emergency Generator
# ──────────────────────────────────────────────────────────────
ROW_6 = {
    "source_id": "S2.001",
    "source_count": 1,
    "new_or_modified": "Yes",
    "system_id": 1,
    "system_desc": "Emergency Power",
    "scc": "2-02-001-02",
    "source_desc": "Emergency Generator (kW \u2264 560; mfg. 2007 or newer)",
    "throughput_unit": "bkW",
    "throughput_material": "diesel",
    "operating_hrs_day": 24,
    "operating_hrs_yr": 100,
    "kW": 560,
    "fuel_type": "diesel",
    "fuel_consumption": 37.55,
    "fuel_unit": "gal",
    "displacement_L": 16.4,
    "cylinders": 8,
    "tier": 3,
    "emission_code": "ECI",
    "spec_reference": "Example: Scania Marine Engines",
    "EF_PM": 0.2,
    "EF_CO": 3.5,
    "EF_NOx": 4,
    "EF_unit": "g/bkW-hr",
    "EF_reference": "40 CFR 1039. Appendix I, Tier 3, 450\u2264kW\u2264560; "
                    "SO2 Mass balance based on 15 ppm S; "
                    "VOC AP-42, Table 3.4-1 (10/96)",
    "ctrl_system": "None",
    "source_type": "POINT",
    "exhaust_temp_F": 1100,
    "acfm": 5429.827606109162,
    "release_reference": "Estimated",
    "cfr_reference": "40 CFR 60, Subpart IIII; 40 CFR 63, Subpart ZZZZ",
    "state_regulation": "NAC 445B.22033, NAC 445B.22024",
    "location_reference": "(LNC 2024c)",
    "NOx_ISR": 0.2,
    "is_emergency": True,
}

# ──────────────────────────────────────────────────────────────
# Row 7: S2.002 Emergency Fire Water Pump
# ──────────────────────────────────────────────────────────────
ROW_7 = {
    "source_id": "S2.002",
    "source_count": 1,
    "new_or_modified": "Yes",
    "system_id": 2,
    "system_desc": "Emergency Fire Water Pump",
    "scc": "2-02-001-02",
    "source_desc": "Emergency Fire Water Pump (75 \u2264 kW < 130; mfg. 2010 or newer)",
    "throughput_unit": "bkW",
    "throughput_material": "diesel",
    "operating_hrs_day": 24,
    "operating_hrs_yr": 100,
    "kW": 129,
    "fuel_type": "diesel",
    "fuel_consumption": 11.6,
    "fuel_unit": "gal",
    "displacement_L": 6.8,
    "cylinders": 6,
    "tier": "N/A",
    "emission_code": "ECI",
    "spec_reference": "Example: Clarke Fire Pump Engines (JU6H-UFABL0)",
    "EF_PM": 0.3,
    "EF_CO": 5,
    "EF_NOx": 4,
    "EF_unit": "g/bkW-hr",
    "EF_reference": "Table 4 to 40 CFR 60, Subpart IIII, 75\u2264kW<130; "
                    "SO2 Mass balance based on 15 ppm S; "
                    "VOC AP-42, Table 3.3-1 (10/96)",
    "ctrl_system": "None",
    "source_type": "POINT",
    "exhaust_temp_F": 908,
    "acfm": 1131,
    "release_reference": "Example: Clarke Fire Pump Engines (JU6H-UFABL0)",
    "cfr_reference": "40 CFR 60, Subpart IIII; 40 CFR 63, Subpart ZZZZ",
    "state_regulation": "NAC 445B.22033, NAC 445B.22024",
    "location_reference": "G. Young (Target) 2/10/25; beside maintenance bldg",
    "NOx_ISR": 0.2,
    "is_emergency": True,
}

# ──────────────────────────────────────────────────────────────
# Propane source template (shared fields for rows 8-24)
# ──────────────────────────────────────────────────────────────
_PROPANE_BASE = {
    "source_count": 1,
    "new_or_modified": "Yes",
    "system_id": "IA",
    "system_desc": "Insignificant Activities",
    "scc": "1-03-010-02",
    "throughput_unit": "kgal",
    "throughput_material": "propane",
    "operating_hrs_day": 24,
    "operating_hrs_yr": 8760,
    "fuel_type": "propane",
    "fuel_unit": "gal",
    "EF_PM": 0.7,
    "EF_CO": 7.5,
    "EF_NOx": 13,
    "EF_unit": "lb/kgal",
    "EF_reference": "AP-42, Table 1.5-1 (07/08) Com. Boilers; SO2 - 15 gr/100ft3",
    "source_type": "POINT",
    "exhaust_temp_F": 360,
    "release_reference": "Ht = bldg +1; Temp, Flow, Dia = Estimated",
    "state_regulation": "NAC 445B.22033, NAC 445B.22030",
    "location_reference": "(LNC 2024c)",
    "NOx_ISR": 0.1,
}


def _propane(source_id, source_desc, fuel_gal_hr, acfm):
    """Build a propane source row dict."""
    d = dict(_PROPANE_BASE)
    d["source_id"] = source_id
    d["source_desc"] = source_desc
    d["fuel_consumption"] = fuel_gal_hr
    d["acfm"] = acfm
    return d


# Rows 8-24: individual propane sources
ROW_8 = _propane("IA1.001-4", "Heaters (4) - Housing Dorm 1 (North)",
                 26.229508196721312, 439.39455658775876)
ROW_9 = _propane("IA1.005-20", "Heaters (16) - Housing Dorm 1 (West)",
                 104.91803278688525, 439.39455658775876)
ROW_10 = _propane("IA1.021-34", "Heaters (14) - Housing Dorm 1 (East)",
                  91.8032786885246, 439.39455658775876)
ROW_11 = _propane("IA1.035-38", "Heaters (4) - Housing Dorm 2",
                  26.229508196721312, 439.39455658775876)
ROW_12 = _propane("IA1.039-55", "Propane Units (17) - Core Kitchen 1",
                  86.33879781420765, 2892.680830869412)
ROW_13 = _propane("IA1.056-61", "Propane Units (6) - Core Kitchen 2",
                  62.48087431693989, 2093.348900010181)
ROW_14 = _propane("IA1.062-69", "Propane Units (8) - Core Diner 1",
                  11.584699453551913, 388.13185831918696)
ROW_15 = _propane("IA1.070-75", "Propane Units (6) - Core Diner 2",
                  7.6502732240437155, 256.31349134285927)
ROW_16 = _propane("IA1.076-78", "Propane Units (3) - Core Rec Center 1",
                  3.497267759562842, 117.17188175673567)
ROW_17 = _propane("IA1.079-80", "Propane Units (2) - Core Rec Center 2",
                  3.0601092896174866, 102.52539653714372)
ROW_18 = _propane("IA1.081-83", "Propane Units (3) - Core Shift Entrance",
                  2.622950819672131, 87.87891131755175)
ROW_19 = _propane("IA1.084", "Propane Unit - Core Gaming Lounge",
                  0.8743169398907105, 29.292970439183918)
ROW_20 = _propane("IA1.085-89", "Propane Units (5) - Core Lounge",
                  7.704918032786885, 258.1443019953083)
ROW_21 = _propane("IA1.090-94", "Propane Units (5) - Core Housekeeping",
                  4.382513661202186, 146.8310143264094)
ROW_22 = _propane("IA1.095-106", "Heaters (12) - Hoteling Facility",
                  28.524590163934427, 955.6831605783754)
ROW_23 = _propane("IA1.107", "Propane Unit - Maintentance",
                  2.185792349726776, 73.2324260979598)
ROW_24 = _propane("IA1.108", "Propane Unit - Core Lobby",
                  2.185792349726776, 73.2324260979598)

# ──────────────────────────────────────────────────────────────
# Row 25: IA1.109 Diesel Storage Tank
# ──────────────────────────────────────────────────────────────
ROW_25 = {
    "source_id": "IA1.109",
    "source_count": 1,
    "new_or_modified": "Yes",
    "system_id": "IA",
    "system_desc": "Insignificant Activities",
    "scc": "4-04-001-99",
    "source_desc": "Diesel tank (20,000 gal)",
    "throughput_unit": "gal",
    "throughput_material": "diesel",
    "operating_hrs_day": 24,
    "operating_hrs_yr": 8760,
    "EF_unit": "lb/yr",
    "EF_reference": "EPA TANKS program",
    "state_regulation": "NAC 445B.22033, NAC 445B.22032",
    "location_reference": "(LNC 2024c)",
}

# ──────────────────────────────────────────────────────────────
# Assemble all rows and populate
# ──────────────────────────────────────────────────────────────
ALL_ROWS = [
    (6, ROW_6),
    (7, ROW_7),
    (8, ROW_8),
    (9, ROW_9),
    (10, ROW_10),
    (11, ROW_11),
    (12, ROW_12),
    (13, ROW_13),
    (14, ROW_14),
    (15, ROW_15),
    (16, ROW_16),
    (17, ROW_17),
    (18, ROW_18),
    (19, ROW_19),
    (20, ROW_20),
    (21, ROW_21),
    (22, ROW_22),
    (23, ROW_23),
    (24, ROW_24),
    (25, ROW_25),
]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    print(f"Template: {TEMPLATE}")
    print(f"Output:   {OUTPUT}")
    print(f"Sources:  {len(ALL_ROWS)} rows (rows 6-25)")
    print()

    result = populate_raw(TEMPLATE, OUTPUT, ALL_ROWS)

    print(f"Workbook populated: {result}")
    print()

    # Summary
    for row_num, data in ALL_ROWS:
        sid = data.get("source_id", "?")
        desc = data.get("source_desc", "?")
        n_fields = sum(1 for v in data.values() if v is not None)
        print(f"  Row {row_num:2d}: {sid:<15s} {desc:<55s} ({n_fields} fields)")


if __name__ == "__main__":
    main()
