import logging
import re
from typing import List, Tuple, Optional

from schema.requests.diagnosis import DiagnosisRequest
from schema.responses.diagnosis import DiagnosisResponse, SymptomSearchResponse

from . import model as ml_service

logger = logging.getLogger(__name__)


def search_symptoms_service(symptom_query: str) -> SymptomSearchResponse:
    """
    Service function to search for symptoms matching user input

    Args:
        symptom_query: User input symptom to search for

    Returns:
        SymptomSearchResponse with matches and exact match flag

    Raises:
        RuntimeError: If models are not loaded
    """
    try:
        logger.info(f"Searching for symptom: {symptom_query}")

        matches, exact_match = ml_service.search_symptoms(symptom_query, max_matches=10)

        logger.info(
            f"Found {len(matches)} matches for '{symptom_query}', exact_match: {exact_match}"
        )

        return SymptomSearchResponse(matches=matches, exact_match=exact_match)

    except Exception as e:
        logger.error(f"Error in symptom search service: {str(e)}")
        raise


def process_diagnosis_request(request: DiagnosisRequest) -> DiagnosisResponse:
    """
    Service function to process a diagnosis request

    Args:
        request: DiagnosisRequest containing symptom information

    Returns:
        DiagnosisResponse with diagnosis results

    Raises:
        RuntimeError: If models are not loaded
        ValueError: If symptom not found in database
    """
    try:
        logger.info(
            f"Processing diagnosis request for symptom: {request.initial_symptom}"
        )

        # Normalize and validate initial symptom
        normalized_symptom = normalize_symptom(request.initial_symptom)

        # Find matching symptom in database
        matching_symptom = find_matching_symptom(normalized_symptom)
        if not matching_symptom:
            raise ValueError(
                f"Symptom '{request.initial_symptom}' not found in database"
            )

        # Get primary diagnosis using decision tree
        primary_diagnosis = ml_service.get_primary_diagnosis(matching_symptom)
        logger.info(f"Primary diagnosis: {primary_diagnosis}")

        # Get secondary diagnosis using all symptoms
        all_symptoms = [matching_symptom] + [
            normalize_symptom(s) for s in request.additional_symptoms
        ]
        # Filter out invalid symptoms
        valid_symptoms = [s for s in all_symptoms if ml_service.validate_symptom(s)]

        secondary_diagnosis = ml_service.get_secondary_diagnosis(valid_symptoms)
        logger.info(f"Secondary diagnosis: {secondary_diagnosis}")

        # Calculate confidence level
        confidence_level = calculate_confidence_level(
            primary_diagnosis, secondary_diagnosis, len(valid_symptoms)
        )

        # Calculate severity assessment
        severity_assessment = ml_service.calculate_severity(
            valid_symptoms, request.days_experiencing
        )

        # Get description and precautions
        description = ml_service.get_disease_description(primary_diagnosis)
        precautions = ml_service.get_disease_precautions(primary_diagnosis)

        # Determine if secondary diagnosis should be included
        include_secondary = (
            secondary_diagnosis != primary_diagnosis
            and secondary_diagnosis != "Unknown"
            and confidence_level == "Moderate"
        )

        response = DiagnosisResponse(
            primary_diagnosis=primary_diagnosis,
            secondary_diagnosis=secondary_diagnosis if include_secondary else None,
            confidence_level=confidence_level,
            description=description,
            precautions=precautions,
            severity_assessment=severity_assessment,
        )

        logger.info(
            f"Diagnosis completed for {request.initial_symptom}: {primary_diagnosis}"
        )
        return response

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error in diagnosis service: {str(e)}")
        raise RuntimeError(f"Error processing diagnosis: {str(e)}")


def normalize_symptom(symptom: str) -> str:
    """
    Normalize symptom string for consistent processing

    Args:
        symptom: Raw symptom string

    Returns:
        Normalized symptom string
    """
    return symptom.strip().replace(" ", "_").lower()


def find_matching_symptom(normalized_symptom: str) -> Optional[str]:
    """
    Find matching symptom in the feature database

    Args:
        normalized_symptom: Normalized symptom string

    Returns:
        Matching symptom from database or None if not found
    """
    available_symptoms = ml_service.get_available_symptoms()

    # Try exact match first
    for symptom in available_symptoms:
        if symptom.lower() == normalized_symptom:
            return symptom

    # Try partial match
    pattern = re.compile(normalized_symptom, re.IGNORECASE)
    for symptom in available_symptoms:
        if pattern.search(symptom.lower()):
            return symptom

    return None


def calculate_confidence_level(
    primary_diagnosis: str, secondary_diagnosis: str, symptom_count: int
) -> str:
    """
    Calculate confidence level based on diagnosis consistency and symptom count

    Args:
        primary_diagnosis: Primary diagnosis result
        secondary_diagnosis: Secondary diagnosis result
        symptom_count: Number of symptoms provided

    Returns:
        Confidence level string
    """
    if primary_diagnosis == secondary_diagnosis:
        if symptom_count >= 3:
            return "High"
        elif symptom_count >= 2:
            return "Moderate"
        else:
            return "Low"
    else:
        if symptom_count >= 4:
            return "Moderate"
        else:
            return "Low"


def get_symptom_suggestions(partial_symptom: str, limit: int = 5) -> List[str]:
    """
    Get symptom suggestions based on partial input

    Args:
        partial_symptom: Partial symptom input
        limit: Maximum number of suggestions

    Returns:
        List of suggested symptoms
    """
    try:
        matches, _ = ml_service.search_symptoms(partial_symptom, max_matches=limit)
        return matches
    except Exception as e:
        logger.error(f"Error getting symptom suggestions: {e}")
        return []


def validate_diagnosis_request(request: DiagnosisRequest) -> Tuple[bool, str]:
    """
    Validate diagnosis request parameters

    Args:
        request: DiagnosisRequest to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if models are loaded
    if not ml_service.is_models_loaded():
        return False, "Medical models are not loaded"

    # Validate initial symptom
    if not request.initial_symptom or not request.initial_symptom.strip():
        return False, "Initial symptom is required"

    # Check if symptom exists in database
    normalized_symptom = normalize_symptom(request.initial_symptom)
    if not find_matching_symptom(normalized_symptom):
        return (
            False,
            f"Symptom '{request.initial_symptom}' not found in medical database",
        )

    # Validate days
    if request.days_experiencing < 1 or request.days_experiencing > 365:
        return False, "Days experiencing symptoms must be between 1 and 365"

    # Validate additional symptoms (optional validation)
    invalid_additional = []
    for symptom in request.additional_symptoms:
        normalized = normalize_symptom(symptom)
        if not find_matching_symptom(normalized):
            invalid_additional.append(symptom)

    if invalid_additional:
        logger.warning(f"Invalid additional symptoms ignored: {invalid_additional}")
        # Don't fail the request, just log the warning

    return True, ""


def get_related_symptoms(disease: str, limit: int = 5) -> List[str]:
    """
    Get symptoms commonly associated with a disease

    Args:
        disease: Disease name
        limit: Maximum number of symptoms to return

    Returns:
        List of related symptoms
    """
    try:
        if not ml_service.is_models_loaded():
            return []

        # This would require additional data or model analysis
        # For now, return empty list as this functionality would need
        # the reduced_data or additional analysis
        return []

    except Exception as e:
        logger.error(f"Error getting related symptoms: {e}")
        return []


def get_diagnosis_statistics() -> dict:
    """
    Get statistics about the diagnosis system

    Returns:
        Dictionary containing system statistics
    """
    try:
        if not ml_service.is_models_loaded():
            return {"error": "Models not loaded"}

        metrics = ml_service.get_model_metrics()

        return {
            "total_symptoms": len(ml_service.get_available_symptoms()),
            "total_diseases": len(ml_service.get_available_diseases()),
            "model_accuracy": {
                "decision_tree": metrics.decision_tree_accuracy if metrics else 0,
                "svm": metrics.svm_accuracy if metrics else 0,
                "cross_validation": metrics.cross_validation_mean if metrics else 0,
            },
            "system_status": (
                "operational" if ml_service.is_models_loaded() else "not_ready"
            ),
        }

    except Exception as e:
        logger.error(f"Error getting diagnosis statistics: {e}")
        return {"error": str(e)}