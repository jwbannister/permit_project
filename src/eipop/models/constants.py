"""Conversion constants from the Conv sheet of the EI workbook.

Values are extracted from the reference workbook and should match
exactly when the template is used. These are physical/regulatory
constants, not project-specific values.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversionConstants:
    """Unit conversion factors and fuel properties."""

    # Time
    sec_per_min: float = 60.0
    sec_per_hr: float = 3600.0
    min_per_hr: float = 60.0
    hr_per_day: float = 24.0
    hr_per_yr: float = 8760.0
    day_per_yr: float = 365.0

    # Mass
    gr_per_lb: float = 7000.0
    g_per_lb: float = 453.592
    kg_per_mt: float = 1000.0
    lb_per_kg: float = 2.20462
    lb_per_ton: float = 2000.0
    kg_per_ton: float = 907.184

    # Length
    in_per_ft: float = 12.0
    ft_per_m: float = 3.28084

    # Temperature
    rankine_at_0F: float = 459.67
    F_standard: float = 68.0
    K_at_0C: float = 273.15
    F_at_0C: float = 32.0
    F_per_C: float = 1.8

    # Power
    hp_per_kW: float = 1.341

    # Energy
    kWhr_per_MMBtu: float = 292.9
    Btu_per_MMBtu: float = 1_000_000.0

    # Diesel fuel properties
    diesel_density_lb_per_gal: float = 7.1
    diesel_sulfur_ppm: float = 15.0  # ULSD
    diesel_Btu_per_gal: float = 140_000.0
    diesel_MMBtu_per_gal: float = 0.14
    diesel_Btu_per_hp_hr: float = 7000.0
    diesel_MMBtu_per_hp_hr: float = 0.007

    # Propane fuel properties
    propane_Btu_per_gal: float = 91_500.0
    propane_MMBtu_per_gal: float = 0.0915
    propane_scf_per_gal: float = 35.65
    propane_lb_per_gal: float = 4.24
    propane_sulfur_gr_per_100scf: float = 15.0  # commercial grade

    # Gasoline fuel properties
    gasoline_lb_per_gal: float = 6.17
    gasoline_MMBtu_per_gal: float = 0.125251

    # Natural gas
    natgas_MMBtu_per_scf: float = 0.001026
    natgas_Btu_per_scf: float = 1020.0
    natgas_Btu_per_hp_hr: float = 9500.0

    # Molecular weights
    MW_SO2: float = 64.0638
    MW_S: float = 32.065
    MW_O: float = 15.9994
    MW_CO: float = 28.01
    MW_H: float = 1.008
    MW_Cl: float = 35.453
    MW_N: float = 14.0067
    MW_air: float = 28.97
    MW_C3H8: float = 44.1

    # Diesel SO2 mass balance result (pre-calculated in Conv sheet)
    # = (15/1e6) * 7.1 * (64.0638/32.065) / 0.14
    diesel_SO2_lb_per_MMBtu: float = 0.0015198580339043461

    # Atmosphere
    atm_standard: float = 1.0


# Singleton instance
CONV = ConversionConstants()
