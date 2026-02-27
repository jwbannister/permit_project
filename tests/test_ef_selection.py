"""Test emission factor selection logic against reference values."""

import pytest

from eipop.calcs.ef_selection import (
    select_emission_factors,
    lb_hp_hr_to_g_kw_hr,
    AP42_DIESEL,
    NSPS_TABLE_4_FIRE_PUMP,
    _lookup_nsps_tier,
)


class TestNspsTierLookup:
    def test_75_to_130_kw(self):
        tier = _lookup_nsps_tier(129.0, NSPS_TABLE_4_FIRE_PUMP)
        assert tier.PM == 0.3
        assert tier.CO == 5.0
        assert tier.NOx_NMHC == 4.0

    def test_130_to_225_kw(self):
        tier = _lookup_nsps_tier(200.0, NSPS_TABLE_4_FIRE_PUMP)
        assert tier.PM == 0.2
        assert tier.CO == 3.5

    def test_boundary_at_130(self):
        """kW=130 falls in the 75-130 range (exclusive upper bound)."""
        tier = _lookup_nsps_tier(130.0, NSPS_TABLE_4_FIRE_PUMP)
        assert tier.label == "75<kW≤130"

    def test_boundary_above_130(self):
        tier = _lookup_nsps_tier(130.1, NSPS_TABLE_4_FIRE_PUMP)
        assert tier.label == "130<kW≤225"

    def test_small_engine(self):
        tier = _lookup_nsps_tier(5.0, NSPS_TABLE_4_FIRE_PUMP)
        assert tier.PM == 0.80
        assert tier.CO == 8.0

    def test_out_of_range(self):
        with pytest.raises(ValueError):
            _lookup_nsps_tier(0.0, NSPS_TABLE_4_FIRE_PUMP)


class TestAP42VocDerivation:
    """Verify the AP-42 VOC factor derivation.

    VOC = TOC Exhaust (2.47E-03 lb/hp-hr) + TOC Crankcase (4.41E-05 lb/hp-hr)
    Converted to g/kW-hr using g/lb × hp/kW.
    """

    def test_voc_lb_hp_hr(self):
        expected = 2.47e-3 + 4.41e-5
        assert AP42_DIESEL.VOC_lb_hp_hr == pytest.approx(expected)

    def test_voc_g_kw_hr(self):
        voc = lb_hp_hr_to_g_kw_hr(AP42_DIESEL.VOC_lb_hp_hr)
        assert voc == pytest.approx(1.5292437428952, rel=1e-10)


class TestSelectEmissionFactors:
    """Test full EF selection for S2.002 fire pump (129 kW diesel)."""

    @pytest.fixture(scope="class")
    def efs(self):
        return select_emission_factors(
            kW=129.0,
            fuel_type="diesel",
            fuel_consumption_gal_hr=11.6,
            is_fire_pump=True,
        )

    def test_pm(self, efs):
        assert efs.PM.value == 0.3
        assert efs.PM.method == "nsps_tier"

    def test_pm10(self, efs):
        assert efs.PM10.value == 0.3

    def test_pm2_5(self, efs):
        assert efs.PM2_5.value == 0.3

    def test_co(self, efs):
        assert efs.CO.value == 5.0

    def test_nox(self, efs):
        assert efs.NOx.value == 4.0

    def test_so2(self, efs):
        assert efs.SO2.value == pytest.approx(0.008678900799931303, rel=1e-6)
        assert efs.SO2.method == "mass_balance"

    def test_voc(self, efs):
        assert efs.VOC.value == pytest.approx(1.5292437428952, rel=1e-10)
        assert efs.VOC.method == "ap42"

    def test_ef_unit(self, efs):
        assert efs.ef_unit == "g/bkW-hr"

    def test_reference_string(self, efs):
        assert "40 CFR 60" in efs.reference
        assert "AP-42" in efs.reference

    def test_unsupported_fuel(self):
        with pytest.raises(NotImplementedError):
            select_emission_factors(kW=100, fuel_type="natural_gas",
                                    fuel_consumption_gal_hr=10.0)


class TestSelectEFsS2001:
    """Test EF selection for S2.001 (560 kW emergency generator).

    Uses AP-42 Table 3.4-1 for VOC (large engine, ≥600 hp).
    """

    @pytest.fixture(scope="class")
    def efs(self):
        return select_emission_factors(
            kW=560.0, fuel_type="diesel", fuel_consumption_gal_hr=37.55,
        )

    def test_pm(self, efs):
        assert efs.PM.value == 0.2

    def test_co(self, efs):
        assert efs.CO.value == 3.5

    def test_nox(self, efs):
        assert efs.NOx.value == 4.0

    def test_voc_uses_table_3_4_1(self, efs):
        assert efs.VOC.value == pytest.approx(0.42882814476, rel=1e-10)
        assert "3.4-1" in efs.VOC.source

    def test_so2(self, efs):
        assert efs.SO2.value == pytest.approx(0.006471699742892123, rel=1e-6)
