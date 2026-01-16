from pydantic import BaseModel, Field, field_validator

class Airport(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Airport name")
    code: str = Field(..., min_length=3, max_length=3, description="Airport code")