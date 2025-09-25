from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated


class DiagnosisInDB(BaseModel):
    id: str
    diagnosed_user_id: Annotated[
        str,
        Field(
            description="The ID of the user who received the diagnosis",
            serialization_alias="diagnosedUserId",
        ),
    ]
    primary_diagnosis: Annotated[
        str,
        Field(
            description="The primary diagnosis", serialization_alias="primaryDiagnosis"
        ),
    ]
    secondary_diagnoses: Annotated[
        list[str],
        Field(
            description="List of secondary diagnoses",
            default_factory=list,
            serialization_alias="secondaryDiagnoses",
        ),
    ]
    description: Annotated[
        str,
        Field(
            description="Detailed description of the diagnosis",
            serialization_alias="description",
        ),
    ]
    precautions: Annotated[
        list[str],
        Field(
            description="List of precautions to be taken",
            default_factory=list,
            serialization_alias="precautions",
        ),
    ]
    severity_assessment: Annotated[
        str,
        Field(
            description="Assessment of the severity of the diagnosis",
            serialization_alias="severityAssessment",
        ),
    ]
    initial_symptom: Annotated[
        str,
        Field(
            description="Initial symptom reported by the user",
            default=None,
            serialization_alias="initialSymptom",
        ),
    ]
    additional_symptoms: Annotated[
        list[str],
        Field(
            description="List of additional symptoms reported by the user",
            default_factory=list,
            serialization_alias="additionalSymptoms",
        ),
    ]
    days_experiencing: Annotated[
        int,
        Field(
            description="Number of days the user has been experiencing symptoms",
            default=0,
            serialization_alias="daysExperiencingSymptoms",
        ),
    ]
    confidence_level: Annotated[
        str,
        Field(
            description="Confidence level of the diagnosis",
            serialization_alias="confidenceLevel",
        ),
    ]


class GetDiagnosisResponse(BaseModel):
    message: str = Field(..., description="Response message")
    diagnosis: DiagnosisInDB = Field(..., description="Detailed diagnosis information")

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
