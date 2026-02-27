"""Test Clarke spec sheet PDF parser against actual reference PDFs."""

from pathlib import Path

import pytest

from eipop.parsers.spec_sheet import (
    parse_spec_sheet,
    get_rated_speed_data,
    _deduplicate_chars,
)

JU6H_PDF = Path("reference/client_docs/Sys2_example_Fire_Pump_ju6h-ufabl0-usa.pdf")
JU4H_PDF = Path("reference/client_docs/Sys2_ju4h-specification-sheet_c133220.pdf")


class TestDeduplicateChars:
    def test_doubled_words(self):
        assert _deduplicate_chars("JJoohhnn DDeeeerree") == "John Deere"

    def test_doubled_numbers(self):
        assert _deduplicate_chars("66006688") == "6068"

    def test_mixed(self):
        assert _deduplicate_chars("JJoohhnn DDeeeerree 66006688 SSeerriieess") == "John Deere 6068 Series"

    def test_normal_text_unchanged(self):
        assert _deduplicate_chars("John Deere") == "John Deere"

    def test_short_word_unchanged(self):
        # Words shorter than 4 chars are left alone (too ambiguous)
        assert _deduplicate_chars("TT A") == "TT A"


@pytest.mark.skipif(not JU6H_PDF.exists(), reason="JU6H spec sheet not available")
class TestJU6HParser:
    @pytest.fixture(scope="class")
    def spec(self):
        return parse_spec_sheet(JU6H_PDF)

    def test_model(self, spec):
        assert spec.model == "JU6H-UFABL0"

    def test_manufacturer(self, spec):
        assert spec.manufacturer == "Clarke"

    def test_engine_series(self, spec):
        assert spec.engine_series == "John Deere 6068 Series"

    def test_cylinders(self, spec):
        assert spec.cylinders == 6

    def test_displacement(self, spec):
        assert spec.displacement_L == 6.8

    def test_aspiration(self, spec):
        assert spec.aspiration == "T"

    def test_exhaust_pipe_diameter(self, spec):
        assert spec.exhaust_pipe_dia_in == 5.0

    def test_ratings_bhp_kw(self, spec):
        assert spec.ratings is not None
        # UFABL0 rated at 173 BHP / 129 kW
        rating = spec.ratings[0]
        assert rating["bhp"] == 173.0
        assert rating["kw"] == 129.0

    def test_io_data_at_2350(self, spec):
        assert spec.io_data is not None
        assert 2350 in spec.io_data
        io = spec.io_data[2350]
        assert io["exhaust_flow_cfm"] == 1131.0
        assert io["exhaust_temp_F"] == 908.0
        assert io["fuel_consumption_gph"] == 11.6

    def test_io_data_at_1760(self, spec):
        io = spec.io_data[1760]
        assert io["exhaust_flow_cfm"] == 885.0
        assert io["exhaust_temp_F"] == 1213.0
        assert io["fuel_consumption_gph"] == 9.6

    def test_io_data_at_2100(self, spec):
        io = spec.io_data[2100]
        assert io["exhaust_flow_cfm"] == 1007.0
        assert io["exhaust_temp_F"] == 964.0
        assert io["fuel_consumption_gph"] == 11.1

    def test_rated_speed_data(self, spec):
        rated = get_rated_speed_data(spec, rated_rpm=2350)
        assert rated["bhp"] == 173.0
        assert rated["kw"] == 129.0
        assert rated["fuel_consumption_gph"] == 11.6
        assert rated["exhaust_temp_F"] == 908.0
        assert rated["exhaust_flow_cfm"] == 1131.0
        assert rated["exhaust_pipe_dia_in"] == 5.0
        assert rated["cylinders"] == 6
        assert rated["displacement_L"] == 6.8


@pytest.mark.skipif(not JU4H_PDF.exists(), reason="JU4H spec sheet not available")
class TestJU4HParser:
    @pytest.fixture(scope="class")
    def spec(self):
        return parse_spec_sheet(JU4H_PDF)

    def test_cylinders(self, spec):
        assert spec.cylinders == 4

    def test_displacement(self, spec):
        assert spec.displacement_L == 4.5

    def test_aspiration(self, spec):
        assert spec.aspiration == "TRWA"

    def test_has_ratings(self, spec):
        assert spec.ratings is not None
        assert len(spec.ratings) > 0
