from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class SymptomSearchResponse(BaseModel):
    matches: List[str] = Field(..., description="List of matching symptoms")
    exact_match: bool = Field(..., description="Whether an exact match was found")


class DiagnosisResponse(BaseModel):
    primary_diagnosis: str = Field(..., description="Primary diagnosis")
    secondary_diagnosis: Optional[str] = Field(
        None, description="Alternative diagnosis if applicable"
    )
    confidence_level: str = Field(..., description="Confidence level of diagnosis")
    description: str = Field(..., description="Description of the diagnosed condition")
    precautions: List[str] = Field(..., description="Recommended precautions")
    severity_assessment: str = Field(
        ..., description="Severity assessment based on symptoms and duration"
    )


class HealthCheckResponse(BaseModel):
    status: str
    message: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    error: str
    details: str
    status_code: int