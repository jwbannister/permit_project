"""Test calculation engine against known reference values for fire pump S2.002.

Reference values are from the actual workbook:
  LN WFH EmisInv_LnPwr_r1_NDEP.xlsm, Proc sheet, row 7.
"""

import math
import pytest

from eipop.calcs.diesel_engine import (
    kw_to_hp,
    fuel_consumption_MMBtu_hr,
    so2_mass_balance_diesel_lb_per_MMBtu,
    so2_ef_g_per_bkWhr,
    stack_velocity_fps,
    temp_F_to_K,
    ft_to_m,
)
from eipop.calcs.emission_rates import calc_hourly_lb, calc_daily_lb, calc_annual_tons, calc_all_rates
from eipop.calcs.model_rates import lb_hr_to_g_s, model_release_params
from eipop.models.constants import CONV

# Tolerance: 0.1% relative error
REL_TOL = 1e-3

# === Fire pump S2.002 reference values ===
# Source: Proc sheet row 7

# Equipment specs
REF_KW = 129.0
REF_HP = 172.989  # =129 * 1.341
REF_FUEL_GAL_HR = 11.6
REF_MMBTU_HR = 1.624  # =11.6 * 0.14
REF_DISP_L = 6.8
REF_CYL = 6
REF_HRS_DAY = 24.0
REF_HRS_YR = 100.0

# Emission factors (g/bkW-hr)
REF_EF_PM = 0.3
REF_EF_PM10 = 0.3
REF_EF_PM2_5 = 0.3
REF_EF_CO = 5.0
REF_EF_NOX = 4.0
REF_EF_SO2 = 0.008678900799931303
REF_EF_VOC = 1.5292437428952

# Hourly emissions (lb/hr)
REF_PM_PPH = 0.08531896506111218
REF_PM10_PPH = 0.08531896506111218
REF_PM2_5_PPH = 0.08531896506111218
REF_CO_PPH = 1.4219827510185366
REF_NOX_PPH = 1.1375862008148292
REF_SO2_PPH = 0.0024682494470606585
REF_VOC_PPH = 0.4349116449

# Daily emissions (lb/day)
REF_PM_PPD = 2.0476551614666927
REF_CO_PPD = 34.127586024444874
REF_NOX_PPD = 27.302068819555902

# Annual emissions (ton/yr)
REF_PM_TPY = 0.004265948253055609
REF_CO_TPY = 0.07109913755092682
REF_NOX_TPY = 0.05687931004074146
REF_SO2_TPY = 0.00012341247235303293
REF_VOC_TPY = 0.021745582245

# Stack / release parameters
REF_REL_HT_FT = 6.0
REF_TEMP_F = 908.0
REF_ACFM = 1131.0
REF_DIA_FT = 0.4166666666666667  # = 5 inches / 12

# Metric release params
REF_REL_HT_M = 1.828799941478402
REF_TEMP_K = 759.8166666666666
REF_VEL_MPS = 42.1365433270641
REF_DIA_M = 0.12699999593600014

# Model emission rates (g/s)
REF_PM10_24_GPS = 0.010750000000000001
REF_CO_ALL_GPS = 0.17916666666666667
REF_NOX_1_GPS = 0.0016362252663622526
REF_SO2_1_GPS = 3.5501591932747915e-06


class TestDieselEngine:
    def test_kw_to_hp(self):
        assert kw_to_hp(REF_KW) == pytest.approx(REF_HP, rel=REL_TOL)

    def test_fuel_mmbtu(self):
        result = fuel_consumption_MMBtu_hr(REF_FUEL_GAL_HR, "diesel")
        assert result == pytest.approx(REF_MMBTU_HR, rel=REL_TOL)

    def test_so2_mass_balance(self):
        result = so2_mass_balance_diesel_lb_per_MMBtu()
        assert result == pytest.approx(CONV.diesel_SO2_lb_per_MMBtu, rel=REL_TOL)

    def test_so2_ef(self):
        result = so2_ef_g_per_bkWhr(REF_KW, REF_FUEL_GAL_HR)
        assert result == pytest.approx(REF_EF_SO2, rel=REL_TOL)

    def test_temp_conversion(self):
        assert temp_F_to_K(REF_TEMP_F) == pytest.approx(REF_TEMP_K, rel=REL_TOL)

    def test_ft_to_m(self):
        assert ft_to_m(REF_REL_HT_FT) == pytest.approx(REF_REL_HT_M, rel=REL_TOL)

    def test_stack_velocity(self):
        vel_fps = stack_velocity_fps(REF_ACFM, REF_DIA_FT)
        vel_mps = vel_fps / CONV.ft_per_m
        assert vel_mps == pytest.approx(REF_VEL_MPS, rel=REL_TOL)

    def test_diameter_conversion(self):
        assert ft_to_m(REF_DIA_FT) == pytest.approx(REF_DIA_M, rel=REL_TOL)


class TestEmissionRates:
    """Test the IFS formula replication for all pollutants."""

    def test_pm_hourly(self):
        result = calc_hourly_lb(REF_EF_PM, "g/bkW-hr", REF_KW, "bkW")
        assert result == pytest.approx(REF_PM_PPH, rel=REL_TOL)

    def test_co_hourly(self):
        result = calc_hourly_lb(REF_EF_CO, "g/bkW-hr", REF_KW, "bkW")
        assert result == pytest.approx(REF_CO_PPH, rel=REL_TOL)

    def test_nox_hourly(self):
        result = calc_hourly_lb(REF_EF_NOX, "g/bkW-hr", REF_KW, "bkW")
        assert result == pytest.approx(REF_NOX_PPH, rel=REL_TOL)

    def test_so2_hourly(self):
        result = calc_hourly_lb(REF_EF_SO2, "g/bkW-hr", REF_KW, "bkW")
        assert result == pytest.approx(REF_SO2_PPH, rel=REL_TOL)

    def test_voc_hourly(self):
        result = calc_hourly_lb(REF_EF_VOC, "g/bkW-hr", REF_KW, "bkW")
        assert result == pytest.approx(REF_VOC_PPH, rel=REL_TOL)

    def test_pm_daily(self):
        pph = calc_hourly_lb(REF_EF_PM, "g/bkW-hr", REF_KW, "bkW")
        ppd = calc_daily_lb(pph, REF_HRS_DAY)
        assert ppd == pytest.approx(REF_PM_PPD, rel=REL_TOL)

    def test_co_daily(self):
        pph = calc_hourly_lb(REF_EF_CO, "g/bkW-hr", REF_KW, "bkW")
        ppd = calc_daily_lb(pph, REF_HRS_DAY)
        assert ppd == pytest.approx(REF_CO_PPD, rel=REL_TOL)

    def test_pm_annual(self):
        pph = calc_hourly_lb(REF_EF_PM, "g/bkW-hr", REF_KW, "bkW")
        tpy = calc_annual_tons(pph, REF_HRS_YR)
        assert tpy == pytest.approx(REF_PM_TPY, rel=REL_TOL)

    def test_co_annual(self):
        pph = calc_hourly_lb(REF_EF_CO, "g/bkW-hr", REF_KW, "bkW")
        tpy = calc_annual_tons(pph, REF_HRS_YR)
        assert tpy == pytest.approx(REF_CO_TPY, rel=REL_TOL)

    def test_nox_annual(self):
        pph = calc_hourly_lb(REF_EF_NOX, "g/bkW-hr", REF_KW, "bkW")
        tpy = calc_annual_tons(pph, REF_HRS_YR)
        assert tpy == pytest.approx(REF_NOX_TPY, rel=REL_TOL)

    def test_so2_annual(self):
        pph = calc_hourly_lb(REF_EF_SO2, "g/bkW-hr", REF_KW, "bkW")
        tpy = calc_annual_tons(pph, REF_HRS_YR)
        assert tpy == pytest.approx(REF_SO2_TPY, rel=REL_TOL)

    def test_voc_annual(self):
        pph = calc_hourly_lb(REF_EF_VOC, "g/bkW-hr", REF_KW, "bkW")
        tpy = calc_annual_tons(pph, REF_HRS_YR)
        assert tpy == pytest.approx(REF_VOC_TPY, rel=REL_TOL)

    def test_calc_all_rates(self):
        """Test the batch calculation for all pollutants."""
        efs = {
            "PM": REF_EF_PM, "PM10": REF_EF_PM10, "PM2.5": REF_EF_PM2_5,
            "CO": REF_EF_CO, "NOx": REF_EF_NOX,
            "SO2": REF_EF_SO2, "VOC": REF_EF_VOC,
        }
        rates = calc_all_rates(efs, "g/bkW-hr", REF_KW, "bkW", REF_HRS_DAY, REF_HRS_YR)

        assert rates["PM"]["pph"] == pytest.approx(REF_PM_PPH, rel=REL_TOL)
        assert rates["CO"]["pph"] == pytest.approx(REF_CO_PPH, rel=REL_TOL)
        assert rates["NOx"]["tpy"] == pytest.approx(REF_NOX_TPY, rel=REL_TOL)
        assert rates["VOC"]["tpy"] == pytest.approx(REF_VOC_TPY, rel=REL_TOL)

    def test_zero_ef(self):
        assert calc_hourly_lb(0.0, "g/bkW-hr", REF_KW, "bkW") == 0.0

    def test_none_ef(self):
        assert calc_hourly_lb(None, "g/bkW-hr", REF_KW, "bkW") == 0.0


class TestModelRates:
    def test_pm10_gps(self):
        pph = calc_hourly_lb(REF_EF_PM10, "g/bkW-hr", REF_KW, "bkW")
        gps = lb_hr_to_g_s(pph)
        assert gps == pytest.approx(REF_PM10_24_GPS, rel=REL_TOL)

    def test_co_gps(self):
        pph = calc_hourly_lb(REF_EF_CO, "g/bkW-hr", REF_KW, "bkW")
        gps = lb_hr_to_g_s(pph)
        assert gps == pytest.approx(REF_CO_ALL_GPS, rel=REL_TOL)

    def test_release_params(self):
        params = model_release_params(REF_REL_HT_FT, REF_TEMP_F, REF_ACFM, REF_DIA_FT)
        assert params["height_m"] == pytest.approx(REF_REL_HT_M, rel=REL_TOL)
        assert params["temp_K"] == pytest.approx(REF_TEMP_K, rel=REL_TOL)
        assert params["velocity_mps"] == pytest.approx(REF_VEL_MPS, rel=REL_TOL)
        assert params["diameter_m"] == pytest.approx(REF_DIA_M, rel=REL_TOL)
