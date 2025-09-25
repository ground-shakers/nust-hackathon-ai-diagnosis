from pydantic import BaseModel, Field, field_validator
from typing import List, Annotated

class DiagnosisRequest(BaseModel):
    """Request model for diagnosing a condition.
    """
    
    initial_symptom: Annotated[str, Field(..., description="Primary symptom experienced")]
    days_experiencing: Annotated[int, Field(..., ge=1, le=365, description="Number of days experiencing symptoms")]
    additional_symptoms: Annotated[List[str], Field(default=[], description="Additional symptoms confirmed by user")]
    user_id: Annotated[str, Field(..., description="Unique identifier for the user")]

class SymptomInput(BaseModel):
    """Input model for symptom search.
    """
    
    symptom: Annotated[str, Field(..., min_length=1, max_length=100, description="Symptom name")]

    @field_validator("symptom")
    def validate_symptom(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Symptom cannot be empty")
        return v.strip().lower()