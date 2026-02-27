"""Clarke fire pump engine spec sheet PDF parser.

Extracts equipment specifications from Clarke JU6H/JU4H series
specification PDFs. The data lives across multiple pages:
  - Page 1: FM-UL ratings table (BHP/kW by model and RPM)
  - Page 1: Specifications table (cylinders, displacement)
  - Pages 4-5: I&O Data (exhaust flow/temp, fuel consumption, pipe dia)

This parser targets the specific layout of Clarke fire pump spec sheets.
Different manufacturer formats would need different parsers.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass
class SpecSheetData:
    """Parsed data from a Clarke spec sheet."""

    model: str = ""
    manufacturer: str = "Clarke"
    engine_series: str = ""
    cylinders: int = 0
    displacement_L: float = 0.0
    aspiration: str = ""

    # Ratings by RPM: {rpm: {"bhp": float, "kw": float}}
    ratings: dict[int, dict[str, float]] | None = None

    # I&O data by RPM: {rpm: {"exhaust_flow_cfm": float, ...}}
    io_data: dict[int, dict[str, float]] | None = None

    # Exhaust pipe diameter (constant across RPMs)
    exhaust_pipe_dia_in: float = 0.0

    # NSPS compliance note
    nsps_note: str = ""


def parse_spec_sheet(pdf_path: str | Path) -> SpecSheetData:
    """Parse a Clarke fire pump spec sheet PDF.

    Args:
        pdf_path: Path to the Clarke spec sheet PDF

    Returns:
        SpecSheetData with extracted values
    """
    pdf_path = Path(pdf_path)
    result = SpecSheetData()

    with pdfplumber.open(pdf_path) as pdf:
        # Extract model from filename or header
        result.model = _extract_model(pdf)

        # Page 1: FM-UL ratings and specifications
        if len(pdf.pages) >= 1:
            page1_text = pdf.pages[0].extract_text() or ""
            result.ratings = _parse_fmul_ratings(page1_text, result.model)
            _parse_specifications(page1_text, result)
            result.nsps_note = _extract_nsps_note(page1_text)

        # Pages 4-5 (indices 3-4): I&O Data
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if "INSTALLATION & OPERATION DATA" in page_text:
                _parse_io_data(page_text, result)

    return result


def _extract_model(pdf: pdfplumber.PDF) -> str:
    """Extract model identifier from the PDF."""
    for page in pdf.pages[:3]:
        text = page.extract_text() or ""
        # Look for "FIRE PUMP MODEL: JU6H-UFABL0" pattern
        match = re.search(r"FIRE PUMP MODEL:\s*(JU[46]H-\S+)", text)
        if match:
            return match.group(1)
        # Look for "ENGINE MODEL JU6H-UFABL0" pattern
        match = re.search(r"ENGINE MODEL\s+(JU[46]H-\S+)", text)
        if match:
            return match.group(1)
    return ""


def _parse_fmul_ratings(text: str, model: str) -> dict[int, dict[str, float]]:
    """Parse the FM-UL ratings table for a specific model.

    The table has RPM columns (1470, 1760, 2100, 2350, 2600, 2800, 3000)
    and rows per model with BHP/kW values.
    """
    ratings = {}

    # Extract the short model code (e.g., "UFABL0" from "JU6H-UFABL0")
    short_model = model.split("-")[-1] if "-" in model else model

    # Parse RPM header line to get column positions
    rpm_columns = [1470, 1760, 2100, 2350, 2600, 2800, 3000]

    # Find lines containing the model code
    for line in text.split("\n"):
        if short_model in line:
            # Strip the model code prefix so it doesn't interfere with
            # numeric extraction. The model code may contain digits
            # (e.g., "UFABL0") that would confuse the regex.
            idx = line.index(short_model) + len(short_model)
            data_part = line[idx:]

            # Extract BHP/kW pairs from the data portion.
            # Each pair is two numbers separated by whitespace: BHP kW
            numbers = re.findall(r"(\d+)\s+(\d+)", data_part)

            # Filter to plausible BHP/kW pairs (BHP > kW, both in range)
            pairs = []
            for first, second in numbers:
                bhp = int(first)
                kw = int(second)
                if 50 < bhp < 500 and 30 < kw < 400 and bhp > kw:
                    pairs.append((float(bhp), float(kw)))

            if not pairs:
                continue

            # Associate pairs with RPM columns. The FM-UL table has 7
            # RPM columns; each model has values only in the columns
            # where it is rated. We can't determine exact column
            # positions from text alone, so store unique pairs.
            seen = set()
            for bhp, kw in pairs:
                key = (bhp, kw)
                if key not in seen:
                    seen.add(key)
                    ratings[len(ratings)] = {"bhp": bhp, "kw": kw}

    return ratings


def _parse_specifications(text: str, result: SpecSheetData) -> None:
    """Parse the Specifications table from page 1."""
    # Number of Cylinders
    match = re.search(r"Number of Cylinders\s+(\d+)", text)
    if match:
        result.cylinders = int(match.group(1))

    # Displacement
    match = re.search(r"Displacement.*?\((\d+\.?\d*)\)", text)
    if match:
        result.displacement_L = float(match.group(1))

    # Aspiration
    match = re.search(r"Aspiration\s+(\w+)", text)
    if match:
        result.aspiration = match.group(1)

    # Engine Series — PDF text may have doubled chars ("EEnnggiinnee SSeerriieess")
    # Try normal text first, then doubled variant
    match = re.search(r"Engine Series\s+(.+?)(?:\n|$)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"EEnnggiinnee SSeerriieess\s+(.+?)(?:\n|$)", text)
    if match:
        raw = match.group(1).strip()
        result.engine_series = _deduplicate_chars(raw)


def _parse_io_data(text: str, result: SpecSheetData) -> None:
    """Parse I&O Data pages for exhaust, fuel, and air system data.

    The I&O pages have a columnar layout with RPM headers (1760, 2100, 2350)
    and rows like:
        Exhaust Flow - ft.³/min (m³/min) ... 885 (25.1)  1007 (28.5)  1131 (32)
        Exhaust Temperature - °F (°C) ...    1213 (656)  964 (518)    908 (487)
        Fuel Consumption - gal/hr (L/hr) ... 9.6 (36.3)  11.1 (42)   11.6 (43.9)
    """
    if result.io_data is None:
        result.io_data = {}

    # RPM headers for the I&O data columns
    rpms = [1760, 2100, 2350]

    # Exhaust Flow
    match = re.search(
        r"Exhaust Flow.*?(\d+)\s*\([^)]+\)\s+(\d+)\s*\([^)]+\)\s+(\d+)",
        text,
    )
    if match:
        for i, rpm in enumerate(rpms):
            if rpm not in result.io_data:
                result.io_data[rpm] = {}
            result.io_data[rpm]["exhaust_flow_cfm"] = float(match.group(i + 1))

    # Exhaust Temperature
    match = re.search(
        r"Exhaust Temperature.*?(\d+)\s*\([^)]+\)\s+(\d+)\s*\([^)]+\)\s+(\d+)",
        text,
    )
    if match:
        for i, rpm in enumerate(rpms):
            if rpm not in result.io_data:
                result.io_data[rpm] = {}
            result.io_data[rpm]["exhaust_temp_F"] = float(match.group(i + 1))

    # Minimum Exhaust Pipe Diameter
    match = re.search(
        r"Minimum Exhaust Pipe Dia.*?(\d+)\s*\((\d+)\)",
        text,
    )
    if match:
        result.exhaust_pipe_dia_in = float(match.group(1))

    # Fuel Consumption
    match = re.search(
        r"Fuel Consumption.*?(\d+\.?\d*)\s*\([^)]+\)\s+(\d+\.?\d*)\s*\([^)]+\)\s+(\d+\.?\d*)",
        text,
    )
    if match:
        for i, rpm in enumerate(rpms):
            if rpm not in result.io_data:
                result.io_data[rpm] = {}
            result.io_data[rpm]["fuel_consumption_gph"] = float(match.group(i + 1))

    # Combustion Air Flow
    match = re.search(
        r"Combustion Air Flow.*?(\d+)\s*\([^)]+\)\s+(\d+)\s*\([^)]+\)\s+(\d+)",
        text,
    )
    if match:
        for i, rpm in enumerate(rpms):
            if rpm not in result.io_data:
                result.io_data[rpm] = {}
            result.io_data[rpm]["air_flow_cfm"] = float(match.group(i + 1))


def _extract_nsps_note(text: str) -> str:
    """Extract the NSPS compliance note from page 1."""
    match = re.search(r"(USA EPA.*?IIII\.?)", text, re.DOTALL)
    if match:
        return match.group(1).replace("\n", " ").strip()
    return ""


def _deduplicate_chars(text: str) -> str:
    """Fix doubled characters from PDF text extraction artifacts.

    Some PDF layouts produce "JJoohhnn DDeeeerree 66006688" instead of
    "John Deere 6068". Deduplicates each word independently since spaces
    between words are not doubled.
    """
    words = text.split()
    result = []
    for word in words:
        if len(word) >= 4 and len(word) % 2 == 0:
            is_doubled = all(word[i] == word[i + 1] for i in range(0, len(word), 2))
            if is_doubled:
                word = word[::2]
        result.append(word)
    return " ".join(result)


def get_rated_speed_data(spec: SpecSheetData, rated_rpm: int = 2350) -> dict[str, float]:
    """Extract data at the rated speed for permitting calculations.

    Args:
        spec: Parsed spec sheet data
        rated_rpm: Engine rated speed (default 2350 for fire pumps)

    Returns:
        Dict with kW, fuel_consumption_gph, exhaust_temp_F,
        exhaust_flow_cfm, exhaust_pipe_dia_in
    """
    result = {}

    # Power rating
    if spec.ratings:
        # Find the rating entry (may not be keyed by exact RPM)
        for key, rating in spec.ratings.items():
            result["bhp"] = rating["bhp"]
            result["kw"] = rating["kw"]
            break  # Use first found (all same for UFABL0)

    # I&O data at rated RPM
    if spec.io_data and rated_rpm in spec.io_data:
        io = spec.io_data[rated_rpm]
        result["fuel_consumption_gph"] = io.get("fuel_consumption_gph", 0.0)
        result["exhaust_temp_F"] = io.get("exhaust_temp_F", 0.0)
        result["exhaust_flow_cfm"] = io.get("exhaust_flow_cfm", 0.0)

    result["exhaust_pipe_dia_in"] = spec.exhaust_pipe_dia_in
    result["cylinders"] = spec.cylinders
    result["displacement_L"] = spec.displacement_L

    return result
