#!/usr/bin/env python3
"""
Startup script for Healthcare Diagnosis API
This script handles environment setup and starts the FastAPI server
"""

import os
import sys
import logging
from pathlib import Path
import uvicorn
from dotenv import load_dotenv


def setup_logging():
    """Configure logging for the application"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "healthcare_api.log")

    # Create logs directory if it doesn't exist
    log_path = Path(log_file).parent
    log_path.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    return logger


def validate_environment():
    """Validate required environment variables and paths"""
    logger = logging.getLogger(__name__)

    # Check required data directories
    data_path = Path(os.getenv("DATA_PATH", "Data/"))
    master_data_path = Path(os.getenv("MASTER_DATA_PATH", "MasterData/"))

    required_files = [
        data_path / "Training.csv",
        data_path / "Testing.csv",
        master_data_path / "symptom_severity.csv",
        master_data_path / "symptom_Description.csv",
        master_data_path / "symptom_precaution.csv",
    ]

    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))

    if missing_files:
        logger.error("Missing required data files:")
        for file_path in missing_files:
            logger.error(f"  - {file_path}")
        logger.error(
            "Please ensure all required data files are present before starting the API"
        )
        return False

    logger.info("Environment validation passed")
    return True


def print_startup_banner():
    """Print startup banner with API information"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                Healthcare Diagnosis API                      ║
    ║              AI-Powered Medical Diagnosis System             ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🏥 Intelligent symptom analysis                            ║
    ║  🧠 Machine learning-based diagnosis                        ║
    ║  📋 Comprehensive health recommendations                    ║
    ║  🔍 Advanced symptom search                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main startup function"""
    # Load environment variables
    load_dotenv()

    # Setup logging
    logger = setup_logging()

    # Print banner
    print_startup_banner()

    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Exiting...")
        sys.exit(1)

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logger.info(f"Starting Healthcare Diagnosis API...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Log Level: {log_level}")

    # Additional startup information
    data_path = os.getenv("DATA_PATH", "Data/")
    master_data_path = os.getenv("MASTER_DATA_PATH", "MasterData/")
    logger.info(f"Data Path: {data_path}")
    logger.info(f"Master Data Path: {master_data_path}")

    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            loop="asyncio",
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()