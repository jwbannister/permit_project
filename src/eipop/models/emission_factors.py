"""Emission factor data model and selection logic."""

from dataclasses import dataclass


@dataclass
class PollutantFactor:
    """Single pollutant emission factor with provenance."""

    value: float
    source: str  # e.g. "40 CFR 60 Subpart IIII, Table 4"
    method: str  # "nsps_tier", "ap42", "mass_balance"


@dataclass
class EmissionFactors:
    """Complete set of emission factors for one source.

    All factors are in the same unit (stored in ef_unit).
    """

    PM: PollutantFactor
    PM10: PollutantFactor
    PM2_5: PollutantFactor
    CO: PollutantFactor
    NOx: PollutantFactor
    SO2: PollutantFactor
    VOC: PollutantFactor
    ef_unit: str  # e.g. "g/bkW-hr", "lb/MMBtu"
    reference: str  # summary citation for the EF set

    def as_dict(self) -> dict[str, float]:
        """Return pollutant name -> factor value mapping."""
        return {
            "PM": self.PM.value,
            "PM10": self.PM10.value,
            "PM2.5": self.PM2_5.value,
            "CO": self.CO.value,
            "NOx": self.NOx.value,
            "SO2": self.SO2.value,
            "VOC": self.VOC.value,
        }
