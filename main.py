import httpx

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError
import logging
from typing import Dict, Any, Annotated
import uvicorn
import os
from contextlib import asynccontextmanager

# Import our modules
from schema.requests.diagnosis import DiagnosisRequest, SymptomInput
from schema.responses.diagnosis import (
    DiagnosisResponse,
    DiagnosisInDB,
    GetDiagnosisResponse,
    SymptomSearchResponse,
    HealthCheckResponse,
    ErrorResponse,
)

from services.diagnosis import (
    search_symptoms_service,
    process_diagnosis_request,
    validate_diagnosis_request,
    get_symptom_suggestions,
    get_diagnosis_statistics,
)

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

from middleware.idempotency import IdempotencyMiddleware

from services import model as ml_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("healthcare_api.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Healthcare Diagnosis API...")
    try:
        # Connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_connection = redis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_connection)

        # Load models and data on startup
        data_path = os.getenv("DATA_PATH", "data/")
        master_data_path = os.getenv("MASTER_DATA_PATH", "master-data/")

        success = ml_service.load_models_and_data(data_path, master_data_path)
        if success:
            logger.info("Models loaded successfully during startup")
        else:
            logger.error("Failed to load models during startup")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't prevent startup, but log the error

    yield

    # Shutdown
    logger.info("Shutting down Healthcare Diagnosis API...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Healthcare Diagnosis API",
    description="AI-powered healthcare diagnosis system using machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    IdempotencyMiddleware,
    ttl_seconds=3600,
    lock_ttl=10,
)


# Dependency to check if models are loaded
def ensure_models_loaded():
    """Dependency to ensure ML models are loaded"""
    if not ml_service.is_models_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models are not loaded. Please wait for initialization to complete.",
        )


# Health Check Endpoints
@app.get(
    "/",
    response_model=HealthCheckResponse,
    tags=["Health Check"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def root() -> HealthCheckResponse:
    """Root endpoint - basic health check"""
    return HealthCheckResponse(
        status="healthy",
        message="Healthcare Diagnosis API is running",
        model_loaded=ml_service.is_models_loaded(),
    )


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health Check"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def health_check() -> HealthCheckResponse:
    """Detailed health check endpoint"""
    model_loaded = ml_service.is_models_loaded()

    return HealthCheckResponse(
        status="healthy" if model_loaded else "initializing",
        message="API is operational" if model_loaded else "ML models are still loading",
        model_loaded=model_loaded,
    )


@app.get(
    "/status",
    tags=["Health Check"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_system_status() -> Dict[str, Any]:
    """Get detailed system status and statistics"""
    try:
        model_status = ml_service.get_model_status()
        statistics = get_diagnosis_statistics()

        return {
            "api_status": "operational",
            "model_status": {
                "loaded": model_status.loaded,
                "last_loaded": model_status.last_loaded,
                "data_path": model_status.data_path,
                "master_data_path": model_status.master_data_path,
            },
            "statistics": statistics,
            "endpoints": {
                "health_check": "/health",
                "symptom_search": "/symptoms/search",
                "diagnosis": "/diagnosis",
                "documentation": "/docs",
            },
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving system status",
        )


# Symptom Search Endpoints
@app.post(
    "/symptoms/search",
    response_model=SymptomSearchResponse,
    tags=["Symptom Management"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_symptoms(
    symptom_input: SymptomInput, _: None = Depends(ensure_models_loaded)
) -> SymptomSearchResponse:
    """
    Search for symptoms matching user input

    - **symptom**: Symptom name to search for (partial matching supported)

    Returns list of matching symptoms and whether an exact match was found.
    """
    try:
        logger.info(f"Symptom search request: {symptom_input.symptom}")

        response = search_symptoms_service(symptom_input.symptom)

        logger.info(f"Symptom search completed: found {len(response.matches)} matches")
        return response

    except Exception as e:
        logger.error(f"Error in symptom search endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching symptoms",
        )


@app.get(
    "/symptoms/suggestions/{partial_symptom}",
    tags=["Symptom Management"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_symptom_suggestions_endpoint(
    partial_symptom: str, limit: int = 5, _: None = Depends(ensure_models_loaded)
) -> Dict[str, Any]:
    """Get symptom suggestions based on partial input"""
    try:
        suggestions = get_symptom_suggestions(partial_symptom, limit)
        return {
            "partial_input": partial_symptom,
            "suggestions": suggestions,
            "count": len(suggestions),
        }
    except Exception as e:
        logger.error(f"Error getting symptom suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting symptom suggestions",
        )


# Diagnosis Endpoints
@app.post(
    "/diagnosis",
    response_model=GetDiagnosisResponse,
    tags=["Diagnosis"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_diagnosis(
    request: DiagnosisRequest, _: None = Depends(ensure_models_loaded)
) -> GetDiagnosisResponse:
    """
    Get medical diagnosis based on symptoms

    - **initial_symptom**: Primary symptom being experienced
    - **days_experiencing**: Number of days symptoms have been present (1-365)
    - **additional_symptoms**: List of additional symptoms (optional)

    Returns comprehensive diagnosis with recommendations.
    """
    try:
        logger.info(
            f"Diagnosis request: {request.initial_symptom}, days: {request.days_experiencing}"
        )

        # Validate the request
        is_valid, error_message = validate_diagnosis_request(request)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

        # Process the diagnosis
        response = process_diagnosis_request(request)
        
        # Create diagnosis on DB
        payload = {
            "primary_diagnosis": response.primary_diagnosis,
            "confidence_level": response.confidence_level,
            "description": response.description,
            "precautions": response.precautions,
            "severity_assessment": response.severity_assessment,
            "secondary_diagnosis": response.secondary_diagnosis,
            "diagnosed_user_id": request.user_id,
            "initial_symptom": request.initial_symptom,
            "days_experiencing": request.days_experiencing,
            "additional_symptoms": request.additional_symptoms,
        }

        api_response = httpx.post("https://ground-shakers.xyz/api/v1/diagnoses", json=payload)
        serialized_response: dict = api_response.json()

        if api_response.status_code != 200:
            logger.error(f"Failed to create diagnosis record: {serialized_response.get('detail', 'Unknown error')}")
        else:
            logger.info(f"Diagnosis record created successfully: {serialized_response}")

        return GetDiagnosisResponse(
            message=serialized_response.get("message", "Diagnosis processed successfully"),
            diagnosis=DiagnosisInDB(**serialized_response.get("diagnosis", {})),
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in diagnosis: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in diagnosis endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing diagnosis request",
        )


# Information Endpoints
@app.get(
    "/symptoms/list",
    tags=["Symptom Management"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def list_all_symptoms(_: None = Depends(ensure_models_loaded)) -> Dict[str, Any]:
    """Get list of all available symptoms"""
    try:
        symptoms = ml_service.get_available_symptoms()
        return {"symptoms": sorted(symptoms), "total_count": len(symptoms)}
    except Exception as e:
        logger.error(f"Error listing symptoms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving symptoms list",
        )


@app.get(
    "/diseases/list",
    tags=["Diseases"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def list_all_diseases(_: None = Depends(ensure_models_loaded)) -> Dict[str, Any]:
    """Get list of all diagnosable diseases"""
    try:
        diseases = ml_service.get_available_diseases()
        return {"diseases": sorted(diseases), "total_count": len(diseases)}
    except Exception as e:
        logger.error(f"Error listing diseases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving diseases list",
        )


@app.get(
    "/statistics",
    tags=["Health Check"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_statistics(_: None = Depends(ensure_models_loaded)) -> Dict[str, Any]:
    """Get system statistics and model performance metrics"""
    try:
        stats = get_diagnosis_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics",
        )

    # Administrative Endpoints


@app.post(
    "/admin/reload-models",
    tags=["Admin"],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def reload_models_endpoint() -> Dict[str, Any]:
    """Reload ML models and data (administrative endpoint)"""
    try:
        logger.info("Manual model reload requested")
        success = ml_service.reload_models()

        if success:
            logger.info("Models reloaded successfully")
            return {
                "status": "success",
                "message": "Models reloaded successfully",
                "timestamp": ml_service.get_model_status().last_loaded,
            }
        else:
            logger.error("Failed to reload models")
            return {"status": "error", "message": "Failed to reload models"}

    except Exception as e:
        logger.error(f"Error reloading models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading models: {str(e)}",
        )


# Error Handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler with detailed error response"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            details=f"HTTP {exc.status_code} error occurred",
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error(f"Validation error: {exc} - Path: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error", details=str(exc), status_code=422
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(
        f"Unhandled exception: {exc} - Path: {request.url.path}", exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            details="An unexpected error occurred",
            status_code=500,
        ).model_dump(),
    )


if __name__ == "__main__":
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )
