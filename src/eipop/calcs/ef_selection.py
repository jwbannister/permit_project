"""Emission factor selection logic.

Applies the regulatory hierarchy to select emission factors for
stationary compression-ignition (diesel) internal combustion engines:

  1. NSPS/CFR standards (40 CFR 60 Subpart IIII → 40 CFR 1039.101)
     — PM, CO, NOx for engines subject to NSPS
  2. Mass balance — SO2 from fuel sulfur content
  3. AP-42 VOC — Table 3.3-1 for industrial engines (<600 hp),
     Table 3.4-1 for large stationary engines (≥600 hp)

References:
  - 40 CFR Part 60, Subpart IIII: Standards for Stationary CI ICE
  - 40 CFR 1039.101: Exhaust emission standards for nonroad CI engines
  - AP-42, Chapter 3.3: Gasoline and Diesel Industrial Engines (10/96)
  - AP-42, Chapter 3.4: Large Stationary Diesel and All Stationary
    Dual-fuel Engines (10/96)
"""

from dataclasses import dataclass

from eipop.models.constants import CONV
from eipop.models.emission_factors import EmissionFactors, PollutantFactor
from eipop.calcs.diesel_engine import so2_ef_g_per_bkWhr


# ──────────────────────────────────────────────────────────────────
# NSPS Tier Standards: 40 CFR 1039.101 Table 1 (for Tier 4 / Final)
# Referenced by 40 CFR 60 Subpart IIII, Table 4
#
# Each row: (kW_min, kW_max, PM, CO, NOx+NMHC) in g/kW-hr
# NOx+NMHC is combined; we assign the full value to NOx since
# NMHC is separately handled via VOC from AP-42.
# ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NspsTier:
    """NSPS emission limits in g/kW-hr for a power range."""
    kW_min: float
    kW_max: float
    PM: float
    CO: float
    NOx_NMHC: float
    label: str


# 40 CFR 60 Subpart IIII, Table 4 — for fire pump engines
# manufactured after 2010-12-31 (Tier 3 equivalent for ≥75 kW)
NSPS_TABLE_4_FIRE_PUMP: list[NspsTier] = [
    NspsTier(kW_min=0, kW_max=8, PM=0.80, CO=8.0, NOx_NMHC=7.5, label="0<kW≤8"),
    NspsTier(kW_min=8, kW_max=19, PM=0.80, CO=6.6, NOx_NMHC=7.5, label="8<kW≤19"),
    NspsTier(kW_min=19, kW_max=37, PM=0.60, CO=5.5, NOx_NMHC=7.5, label="19<kW≤37"),
    NspsTier(kW_min=37, kW_max=75, PM=0.40, CO=5.0, NOx_NMHC=4.7, label="37<kW≤75"),
    NspsTier(kW_min=75, kW_max=130, PM=0.30, CO=5.0, NOx_NMHC=4.0, label="75<kW≤130"),
    NspsTier(kW_min=130, kW_max=225, PM=0.20, CO=3.5, NOx_NMHC=4.0, label="130<kW≤225"),
    NspsTier(kW_min=225, kW_max=450, PM=0.20, CO=3.5, NOx_NMHC=4.0, label="225<kW≤450"),
    NspsTier(kW_min=450, kW_max=560, PM=0.20, CO=3.5, NOx_NMHC=4.0, label="450<kW≤560"),
    NspsTier(kW_min=560, kW_max=999999, PM=0.20, CO=3.5, NOx_NMHC=4.0, label="kW>560"),
]


# ──────────────────────────────────────────────────────────────────
# AP-42 Table 3.3-1: Diesel fuel emission factors
# SCC 2-02-001-02, 2-03-001-01
# ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AP42DieselFactors:
    """AP-42 Table 3.3-1 diesel emission factors in lb/hp-hr."""
    NOx: float = 0.031
    CO: float = 6.68e-3
    SOx: float = 2.05e-3
    PM10: float = 2.20e-3
    TOC_exhaust: float = 2.47e-3
    TOC_crankcase: float = 4.41e-5
    Aldehydes: float = 4.63e-4

    @property
    def VOC_lb_hp_hr(self) -> float:
        """Total VOC = TOC exhaust + crankcase."""
        return self.TOC_exhaust + self.TOC_crankcase


AP42_DIESEL = AP42DieselFactors()


# ──────────────────────────────────────────────────────────────────
# AP-42 Table 3.4-1: Large stationary diesel engine emission factors
# For engines ≥600 hp. Chapter 3.4 (10/96).
# TOC = 0.10 lb/MMBtu (fuel input basis).
# At standard BSFC of 7000 Btu/hp-hr: 0.10 * 7000/1e6 = 7.0e-4 lb/hp-hr
# Plus crankcase contribution of 5.0e-6 lb/hp-hr = total 7.05e-4 lb/hp-hr
# ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AP42LargeDieselFactors:
    """AP-42 Table 3.4-1 large diesel emission factors in lb/hp-hr."""
    TOC_exhaust: float = 7.0e-4
    TOC_crankcase: float = 5.0e-6

    @property
    def VOC_lb_hp_hr(self) -> float:
        """Total VOC = TOC exhaust + crankcase."""
        return self.TOC_exhaust + self.TOC_crankcase


AP42_LARGE_DIESEL = AP42LargeDieselFactors()

# Boundary between Table 3.3-1 and 3.4-1 (in hp)
_LARGE_ENGINE_HP_THRESHOLD = 600


def lb_hp_hr_to_g_kw_hr(val: float) -> float:
    """Convert lb/hp-hr to g/kW-hr using Conv sheet constants."""
    return val * CONV.g_per_lb * CONV.hp_per_kW


def select_emission_factors(
    kW: float,
    fuel_type: str,
    fuel_consumption_gal_hr: float,
    is_fire_pump: bool = False,
) -> EmissionFactors:
    """Select emission factors using the regulatory hierarchy.

    For NSPS-subject diesel CI engines (fire pumps, emergency generators):
      - PM, PM10, PM2.5, CO, NOx → 40 CFR 60 Subpart IIII Table 4
      - SO2 → mass balance from fuel sulfur content
      - VOC → AP-42 Table 3.3-1 (TOC exhaust + crankcase)

    Args:
        kW: Brake power rating in kilowatts
        fuel_type: Fuel type ("diesel")
        fuel_consumption_gal_hr: Fuel consumption in gallons per hour
        is_fire_pump: True for fire pump engines (Table 4 applies)

    Returns:
        EmissionFactors with all 7 pollutants populated
    """
    if fuel_type != "diesel":
        raise NotImplementedError(f"Only diesel fuel supported, got: {fuel_type}")

    # Step 1: NSPS Tier lookup (PM, CO, NOx)
    tier = _lookup_nsps_tier(kW, NSPS_TABLE_4_FIRE_PUMP)
    nsps_source = f"40 CFR 60 Subpart IIII Table 4, {tier.label}"

    pm_ef = tier.PM
    co_ef = tier.CO
    nox_ef = tier.NOx_NMHC  # Assign full NOx+NMHC to NOx column

    # Step 2: SO2 mass balance
    so2_ef = so2_ef_g_per_bkWhr(kW, fuel_consumption_gal_hr)
    so2_source = f"Mass balance, {CONV.diesel_sulfur_ppm} ppm S diesel"

    # Step 3: VOC from AP-42
    # Engines ≥600 hp use Table 3.4-1 (large stationary diesel)
    # Engines <600 hp use Table 3.3-1 (industrial diesel)
    hp = kW * CONV.hp_per_kW
    if hp >= _LARGE_ENGINE_HP_THRESHOLD:
        voc_ef = lb_hp_hr_to_g_kw_hr(AP42_LARGE_DIESEL.VOC_lb_hp_hr)
        voc_source = "AP-42 Table 3.4-1 (TOC exhaust + crankcase)"
        voc_ref = "VOC AP-42, Table 3.4-1 (10/96)"
    else:
        voc_ef = lb_hp_hr_to_g_kw_hr(AP42_DIESEL.VOC_lb_hp_hr)
        voc_source = "AP-42 Table 3.3-1 (TOC exhaust + crankcase)"
        voc_ref = "VOC AP-42, Table 3.3-1 (10/96)"

    ref_parts = [
        f"Table 4 to 40 CFR 60, Subpart IIII, {tier.label}",
        f"SO2 Mass balance based on {CONV.diesel_sulfur_ppm} ppm S",
        voc_ref,
    ]

    return EmissionFactors(
        PM=PollutantFactor(pm_ef, nsps_source, "nsps_tier"),
        PM10=PollutantFactor(pm_ef, nsps_source, "nsps_tier"),
        PM2_5=PollutantFactor(pm_ef, nsps_source, "nsps_tier"),
        CO=PollutantFactor(co_ef, nsps_source, "nsps_tier"),
        NOx=PollutantFactor(nox_ef, nsps_source, "nsps_tier"),
        SO2=PollutantFactor(so2_ef, so2_source, "mass_balance"),
        VOC=PollutantFactor(voc_ef, voc_source, "ap42"),
        ef_unit="g/bkW-hr",
        reference="; ".join(ref_parts),
    )


def _lookup_nsps_tier(kW: float, table: list[NspsTier]) -> NspsTier:
    """Find the NSPS tier row for a given power rating."""
    for tier in table:
        if tier.kW_min < kW <= tier.kW_max:
            return tier
    raise ValueError(f"No NSPS tier found for {kW} kW")
