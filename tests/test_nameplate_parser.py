"""Test nameplate photo parser using Claude vision API.

These tests require:
1. ANTHROPIC_API_KEY environment variable set
2. Reference nameplate photo in reference/client_docs/
"""

import os
from pathlib import Path

import pytest

from eipop.parsers.nameplate import parse_nameplate, _to_nameplate_data

NAMEPLATE_JPG = Path("reference/client_docs/FirePump_PXL_20260211_174608163.jpg")

has_api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

_skip_api = pytest.mark.skipif(
    not (NAMEPLATE_JPG.exists() and has_api_key),
    reason="Nameplate photo or ANTHROPIC_API_KEY not available",
)


@_skip_api
class TestNameplateParser:
    @pytest.fixture(scope="class")
    def result(self):
        return parse_nameplate(NAMEPLATE_JPG)

    def test_manufacturer(self, result):
        assert "CLARKE" in result.manufacturer.upper()

    def test_model(self, result):
        assert result.model == "JU4H-UFADP0"

    def test_serial_number(self, result):
        assert result.serial_number == "SO212287P"

    def test_esn(self, result):
        assert result.esn == "PE4045N053222"

    def test_bhp(self, result):
        assert result.bhp_from == 130.0
        assert result.bhp_to == 130.0

    def test_rated_rpm(self, result):
        assert result.rated_rpm == 2350

    def test_mfg_date(self, result):
        assert result.mfg_month == 6
        assert result.mfg_year == 2025


class TestToNameplateData:
    """Test the JSON-to-dataclass conversion (no API call needed)."""

    def test_full_conversion(self):
        data = {
            "manufacturer": "CLARKE",
            "model": "JU4H-UFADP0",
            "serial_number": "SO212287P",
            "esn": "PE4045N053222",
            "bhp_from": 130,
            "bhp_to": 130,
            "rated_rpm": 2350,
            "mfg_month": 6,
            "mfg_year": 2025,
            "battery_vdc": 12,
            "heater_vac": 115,
            "raw_text": "CLARKE nameplate text",
        }
        result = _to_nameplate_data(data)
        assert result.manufacturer == "CLARKE"
        assert result.model == "JU4H-UFADP0"
        assert result.bhp_from == 130.0
        assert result.mfg_year == 2025

    def test_handles_nulls(self):
        data = {
            "manufacturer": "CLARKE",
            "model": None,
            "serial_number": None,
            "esn": None,
            "bhp_from": None,
            "bhp_to": None,
            "rated_rpm": None,
            "mfg_month": None,
            "mfg_year": None,
            "battery_vdc": None,
            "heater_vac": None,
            "raw_text": None,
        }
        result = _to_nameplate_data(data)
        assert result.manufacturer == "CLARKE"
        assert result.model == ""
        assert result.bhp_from == 0.0
        assert result.mfg_year == 0
