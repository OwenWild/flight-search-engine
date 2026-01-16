from pydantic import BaseModel, Field, field_validator
from datetime import date

from data.Airport import Airport


class FlightSearchQuery(BaseModel):
    origin: Airport = Field(...)
    destination: str = Field(..., min_length=3, max_length=3, description="IATA code for destination airport")
    departure_date: date = Field(..., description="Date of departure (YYYY-MM-DD)")

