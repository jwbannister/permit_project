"""AERMOD model-ready emission rate and release parameter conversions.

Converts emission rates from lb/hr to g/s and release parameters
from imperial to metric for AERMOD input files.
"""

from eipop.models.constants import CONV
from eipop.calcs.diesel_engine import temp_F_to_K, ft_to_m, stack_velocity_fps


def lb_hr_to_g_s(lb_hr: float) -> float:
    """Convert lb/hr to g/s for AERMOD emission rates."""
    return lb_hr * CONV.g_per_lb / CONV.sec_per_hr


def ton_yr_to_g_s(ton_yr: float) -> float:
    """Convert ton/yr to g/s for AERMOD emission rates."""
    return ton_yr * CONV.lb_per_ton * CONV.g_per_lb / (CONV.hr_per_yr * CONV.sec_per_hr)


def model_release_params(
    release_height_ft: float,
    exhaust_temp_F: float,
    acfm: float,
    diameter_ft: float,
) -> dict[str, float]:
    """Calculate AERMOD release parameters in metric units.

    Returns:
        Dict with keys: height_m, temp_K, velocity_mps, diameter_m
    """
    velocity_fps = stack_velocity_fps(acfm, diameter_ft)
    return {
        "height_m": ft_to_m(release_height_ft),
        "temp_K": temp_F_to_K(exhaust_temp_F),
        "velocity_mps": velocity_fps / CONV.ft_per_m,
        "diameter_m": ft_to_m(diameter_ft),
    }


def emergency_model_pph(tpy: float) -> float:
    """Convert annual tons to model lb/hr for emergency sources.

    Emergency equipment (e.g. fire pumps, 100 hr/yr) uses annualized
    emission rates for modeling: spread the annual tons over 8760 hrs.
    Formula: tpy * 2000 lb/ton / 8760 hr/yr

    This replicates the Proc sheet CO/CP column formulas:
        CO7 = BG7 * $I$31 / $M$34  (for emergency sources)
    """
    return tpy * CONV.lb_per_ton / CONV.hr_per_yr


def model_emission_rates(
    rates: dict[str, dict[str, float]],
    is_emergency: bool = False,
    nox_isr: float = 1.0,
) -> dict[str, float]:
    """Convert emission rates to g/s for AERMOD modeling scenarios.

    For non-emergency sources, all scenarios use the hourly rate (lb/hr → g/s).

    For emergency sources, the Proc sheet applies special logic:
    - CO7 (model NOx lb/hr) = NOx_tpy * lb/ton / hr/yr (annualized)
    - CP7 (model SO2 lb/hr) = SO2_tpy * lb/ton / hr/yr (annualized)
    - CC/CD (1-hr g/s) = CO7 or CP7 converted to g/s
    - CF/CG/CH (annual g/s) = tpy * lb/ton / (hr/yr * sec/hr) * g/lb (=ton_yr_to_g_s)
    - Short-term scenarios (PM10-24, PM2.5-24, CO-ALL, SO2-ST) use hourly rates

    The NOx ISR (in-stack ratio) is applied to the model NOx rate.

    Returns:
        Dict keyed by model scenario ID, plus model_NOx_pph and model_SO2_pph
    """
    if is_emergency:
        # Model NOx/SO2 lb/hr: annualized from tpy
        model_nox_pph = emergency_model_pph(rates["NOx"]["tpy"])
        model_so2_pph = emergency_model_pph(rates["SO2"]["tpy"])
    else:
        # Non-emergency: use actual hourly rate
        # ISR is stored as a parameter for AERMOD but does not reduce
        # the model lb/hr or g/s values in the Proc sheet.
        model_nox_pph = rates["NOx"]["pph"]
        model_so2_pph = rates["SO2"]["pph"]

    result = {
        # Short-term scenarios: always use hourly rate
        "PM10_24_gps": lb_hr_to_g_s(rates["PM10"]["pph"]),
        "PM2_5_24_gps": lb_hr_to_g_s(rates["PM2.5"]["pph"]),
        "CO_ALL_gps": lb_hr_to_g_s(rates["CO"]["pph"]),
        "SO2_ST_gps": lb_hr_to_g_s(rates["SO2"]["pph"]),

        # 1-hr scenarios: use model NOx/SO2 (annualized for emergency)
        "NOx_1_gps": lb_hr_to_g_s(model_nox_pph),
        "SO2_1_gps": lb_hr_to_g_s(model_so2_pph),

        # Annual scenarios: use ton/yr → g/s (spreads over 8760 hrs)
        "PM2_5_AN_gps": ton_yr_to_g_s(rates["PM2.5"]["tpy"]),
        "NOx_AN_gps": lb_hr_to_g_s(model_nox_pph),
        "SO2_AN_gps": lb_hr_to_g_s(model_so2_pph),

        # Model lb/hr values (written to CO/CP columns)
        "NOx_model_pph": model_nox_pph,
        "SO2_model_pph": model_so2_pph,
    }
    return result
