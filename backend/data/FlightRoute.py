from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class FlightRoute:
    """Represents a single search combination of origin, destination and date"""
    origin: str
    destination: str
    date: date