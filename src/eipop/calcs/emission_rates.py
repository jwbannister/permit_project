"""Emission rate calculations replicating the Proc sheet IFS formula.

The master IFS formula handles multiple emission factor unit types:
  - g/bkW-hr (diesel engines via throughput)
  - lb/hr (direct hourly rate)
  - lb/yr (annual rate divided by hours)
  - gr/dscf (grains per dry standard cubic foot)

Each pollutant flows through: EF → hourly (lb/hr) → daily (lb/day) → annual (ton/yr)
"""

from eipop.models.constants import CONV


def calc_hourly_lb(
    ef: float | None,
    ef_unit: str,
    throughput_hr: float,
    throughput_unit: str,
    ctrl_eff: float = 0.0,
    hrs_yr: float = 8760.0,
    dscfm: float = 0.0,
) -> float:
    """Calculate hourly emission rate in lb/hr.

    Replicates the Proc sheet IFS/array formula for columns AO-AU.

    Args:
        ef: Emission factor value
        ef_unit: Unit string, e.g. "g/bkW-hr", "lb/hr", "lb/yr", "gr/dscf"
        throughput_hr: Hourly throughput in throughput_unit (e.g. kW for engines)
        throughput_unit: Throughput unit string, e.g. "bkW"
        ctrl_eff: Control efficiency (0.0 = no control, 0.5 = 50%)
        hrs_yr: Operating hours per year
        dscfm: Dry standard cubic feet per minute (for gr/dscf path)

    Returns:
        Emission rate in lb/hr
    """
    if ef is None or not isinstance(ef, (int, float)) or ef == 0:
        return 0.0

    if ef_unit == "lb/hr":
        return ef * (1 - ctrl_eff)

    if ef_unit == "lb/yr":
        return ef / hrs_yr * (1 - ctrl_eff)

    if ef_unit == "gr/dscf":
        return ef * dscfm * CONV.min_per_hr / CONV.gr_per_lb

    # Generic throughput path: "bkW" found in "g/bkW-hr", etc.
    if throughput_unit in ef_unit:
        if ef_unit.startswith("g/"):
            divisor = CONV.g_per_lb  # 453.592
        else:
            divisor = 1.0
        return ef * throughput_hr * (1 - ctrl_eff) / divisor

    return 0.0


def calc_daily_lb(hourly_lb: float, hrs_day: float) -> float:
    """Calculate daily emission rate in lb/day."""
    return hourly_lb * hrs_day


def calc_annual_tons(hourly_lb: float, hrs_yr: float) -> float:
    """Calculate annual emission rate in ton/yr."""
    return hourly_lb * hrs_yr / CONV.lb_per_ton


POLLUTANTS = ["PM", "PM10", "PM2.5", "CO", "NOx", "SO2", "VOC"]


def calc_all_rates(
    emission_factors: dict[str, float],
    ef_unit: str,
    throughput_hr: float,
    throughput_unit: str,
    hrs_day: float,
    hrs_yr: float,
    ctrl_eff: float = 0.0,
    dscfm: float = 0.0,
) -> dict[str, dict[str, float]]:
    """Calculate emission rates for all pollutants and time periods.

    Returns:
        Dict keyed by pollutant, each containing:
            {"pph": lb/hr, "ppd": lb/day, "tpy": ton/yr}
    """
    results = {}
    for pollutant in POLLUTANTS:
        ef = emission_factors.get(pollutant, 0.0)
        pph = calc_hourly_lb(ef, ef_unit, throughput_hr, throughput_unit, ctrl_eff, hrs_yr, dscfm)
        ppd = calc_daily_lb(pph, hrs_day)
        tpy = calc_annual_tons(pph, hrs_yr)
        results[pollutant] = {"pph": pph, "ppd": ppd, "tpy": tpy}
    return results
