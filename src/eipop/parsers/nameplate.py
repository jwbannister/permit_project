"""Equipment nameplate photo parser using Claude vision API.

Extracts structured equipment data from a photograph of an equipment
nameplate/data plate. This is the most reliable source for:
  - Exact model number (as installed)
  - Serial number / ESN
  - BHP rating and rated RPM
  - Manufacture date (month/year)

These values may differ from the spec sheet (which covers a family
of models) and are authoritative for the specific installed unit.
"""

import base64
import json
from dataclasses import dataclass
from pathlib import Path

import anthropic


@dataclass
class NameplateData:
    """Structured data extracted from an equipment nameplate photo."""

    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    esn: str = ""

    # Power ratings
    bhp_from: float = 0.0
    bhp_to: float = 0.0
    rated_rpm: int = 0

    # Manufacture date
    mfg_month: int = 0
    mfg_year: int = 0

    # Electrical
    battery_vdc: int = 0
    heater_vac: int = 0

    # Raw text (for audit trail)
    raw_text: str = ""


_EXTRACTION_PROMPT = """\
This is a photograph of an equipment nameplate/data plate, typically found on
diesel engines, fire pumps, generators, or similar industrial equipment.

Extract ALL text and data from the nameplate into a JSON object with these
fields (use null for any field not visible or not applicable):

{
  "manufacturer": "Company name",
  "location": "City, State, Country from nameplate",
  "description": "Equipment description text",
  "model": "Full model number",
  "serial_number": "Manufacturing serial number (MFG S/N)",
  "esn": "Engine serial number (ESN)",
  "bhp_from": numeric BHP in FROM rating,
  "bhp_to": numeric BHP in UP TO rating,
  "rated_rpm": numeric RPM,
  "battery_vdc": numeric battery voltage,
  "heater_vac": numeric heater voltage,
  "mfg_month": numeric manufacture month (1-12),
  "mfg_year": numeric manufacture year (4 digits),
  "certifications": ["list of certification marks visible"],
  "raw_text": "Complete transcription of all text on the nameplate"
}

Return ONLY the JSON object, no other text."""


def parse_nameplate(
    image_path: str | Path,
    model: str = "claude-haiku-4-5-20251001",
) -> NameplateData:
    """Parse an equipment nameplate photo using Claude vision.

    Args:
        image_path: Path to the nameplate photo (JPG/PNG)
        model: Claude model to use (haiku is fast and sufficient for OCR)

    Returns:
        NameplateData with extracted values
    """
    image_path = Path(image_path)
    image_bytes = image_path.read_bytes()
    b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")

    suffix = image_path.suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": _EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text
    # Strip markdown code fences if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    data = json.loads(response_text)
    return _to_nameplate_data(data)


def _to_nameplate_data(data: dict) -> NameplateData:
    """Convert raw JSON dict to NameplateData."""
    return NameplateData(
        manufacturer=data.get("manufacturer") or "",
        model=data.get("model") or "",
        serial_number=data.get("serial_number") or "",
        esn=data.get("esn") or "",
        bhp_from=float(data["bhp_from"]) if data.get("bhp_from") else 0.0,
        bhp_to=float(data["bhp_to"]) if data.get("bhp_to") else 0.0,
        rated_rpm=int(data["rated_rpm"]) if data.get("rated_rpm") else 0,
        mfg_month=int(data["mfg_month"]) if data.get("mfg_month") else 0,
        mfg_year=int(data["mfg_year"]) if data.get("mfg_year") else 0,
        battery_vdc=int(data["battery_vdc"]) if data.get("battery_vdc") else 0,
        heater_vac=int(data["heater_vac"]) if data.get("heater_vac") else 0,
        raw_text=data.get("raw_text") or "",
    )
