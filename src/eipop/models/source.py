"""Source specification data model."""

from dataclasses import dataclass, field


@dataclass
class SourceSpec:
    """Equipment source specification extracted from client documents.

    Represents one emission source (one row in the Proc sheet).
    """

    # Identification
    source_id: str  # e.g. "S2.002"
    source_count: int = 1
    new_or_modified: str = "Yes"
    system_id: int = 0  # system number
    system_desc: str = ""
    scc: str = ""  # Source Classification Code
    source_desc: str = ""

    # Equipment specs
    manufacturer: str = ""
    model: str = ""
    kW: float = 0.0
    fuel_type: str = ""  # "diesel", "propane", "natural gas"
    fuel_consumption: float = 0.0  # fuel throughput per hour
    fuel_unit: str = ""  # "gal", "scf", etc.
    displacement_L: float = 0.0
    cylinders: int = 0
    tier: str = ""  # "N/A", "Tier 1", "Tier 2", etc.

    # Operating parameters
    operating_hrs_day: float = 24.0
    operating_hrs_yr: float = 100.0
    is_emergency: bool = False

    # Throughput
    throughput_unit: str = ""  # "bkW", "MMBtu", etc.

    # Stack / release parameters
    source_type: str = "POINT"  # "POINT" or "VOLUME"
    release_height_ft: float = 0.0
    exhaust_temp_F: float = 0.0
    exhaust_flow_acfm: float = 0.0
    stack_diameter_ft: float = 0.0

    # Location
    utm_easting: float = 0.0
    utm_northing: float = 0.0
    elevation_m: float = 0.0

    # References
    equipment_reference: str = ""
    location_reference: str = ""
    elevation_reference: str = ""
    spec_reference: str = ""

    # Regulatory
    cfr_reference: str = ""
    state_regulation: str = ""
    emission_code: str = ""  # "ECI" etc.

    # NOx in-stack ratio
    nox_isr: float = 0.0
    nox_isr_reference: str = ""

    @property
    def hp(self) -> float:
        """Horsepower from kW using standard conversion."""
        return self.kW * 1.341

    @property
    def throughput_hr(self) -> float:
        """Hourly throughput in throughput units (typically kW for engines)."""
        return self.kW

    @property
    def throughput_day(self) -> float:
        return self.throughput_hr * self.operating_hrs_day

    @property
    def throughput_yr(self) -> float:
        return self.throughput_hr * self.operating_hrs_yr
