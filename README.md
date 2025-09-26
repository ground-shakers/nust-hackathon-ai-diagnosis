# Healthcare Diagnosis API

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.117+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)

An enterprise-grade AI-powered healthcare diagnosis system built with FastAPI and scikit-learn that provides intelligent symptom analysis, medical recommendations, and comprehensive health assessments.

## 🚀 Features

### Core Functionality
- **🧠 AI-Powered Diagnosis**: Machine learning-based medical diagnosis using Decision Trees and Support Vector Machines (SVM)
- **🔍 Intelligent Symptom Search**: Advanced fuzzy matching algorithms for symptom queries with partial text support
- **📊 Severity Assessment**: Dynamic risk evaluation based on symptoms, duration, and medical severity scores
- **🎯 Confidence Scoring**: Multi-factor confidence calculation considering symptom consistency and count
- **📋 Comprehensive Precautions**: Evidence-based medical precautions and recommendations

### Technical Features
- **⚡ High Performance**: Asynchronous request handling with Redis-backed rate limiting
- **🔒 Security First**: Input validation, idempotency middleware, and secure error handling
- **📈 Monitoring & Analytics**: Real-time system metrics, model performance tracking, and health monitoring
- **🐳 Docker Ready**: Complete containerization with Docker Compose orchestration
- **🌐 Production Ready**: CORS support, comprehensive logging, and graceful error handling
- **🔄 Auto-Recovery**: Model hot-reloading and graceful degradation capabilities

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Load Balancer  │    │     Redis       │
│                 │    │                  │    │   (Caching &    │
│ Web/Mobile/CLI  │◄──►│   (Optional)     │    │  Rate Limiting) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌────────▼────────┐              │
                       │   FastAPI App   │◄─────────────┘
                       │                 │
                       │ • Authentication │
                       │ • Rate Limiting  │
                       │ • Validation     │
                       │ • Error Handling │
                       └────────┬────────┘
                                │
                    ┌───────────▼────────────┐
                    │   ML Service Layer     │
                    │                        │
                    │ • Decision Tree Model  │
                    │ • SVM Classifier       │
                    │ • Symptom Matcher      │
                    │ • Severity Calculator  │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Data Layer           │
                    │                        │
                    │ • Training Data        │
                    │ • Master Data          │
                    │ • Model Artifacts      │
                    │ • External API         │
                    └────────────────────────┘
```

## 📋 API Endpoints

### 🏥 Health & System Monitoring

| Endpoint | Method | Description | Response Model |
|----------|--------|-------------|----------------|
| `/` | GET | Basic API health check | `HealthCheckResponse` |
| `/health` | GET | Detailed health status with model loading info | `HealthCheckResponse` |
| `/status` | GET | Comprehensive system metrics and statistics | `Dict[str, Any]` |

### 🔍 Symptom Management

| Endpoint | Method | Description | Response Model |
|----------|--------|-------------|----------------|
| `/symptoms/search` | POST | Advanced symptom search with fuzzy matching | `SymptomSearchResponse` |
| `/symptoms/suggestions/{partial}` | GET | Get autocomplete suggestions for symptoms | `Dict[str, Any]` |
| `/symptoms/list` | GET | Retrieve all available symptoms in the system | `Dict[str, Any]` |

### 🩺 Medical Diagnosis

| Endpoint | Method | Description | Response Model |
|----------|--------|-------------|----------------|
| `/diagnosis` | POST | Get AI-powered medical diagnosis | `GetDiagnosisResponse` |
| `/diseases/list` | GET | List all diagnosable diseases | `Dict[str, Any]` |
| `/statistics` | GET | Get diagnostic statistics and model metrics | `Dict[str, Any]` |

### ⚙️ Administration

| Endpoint | Method | Description | Response Model |
|----------|--------|-------------|----------------|
| `/admin/reload-models` | POST | Hot-reload ML models without downtime | `Dict[str, Any]` |

## 🛠️ Installation & Setup

### Prerequisites

- **Python**: 3.13+ (recommended) or 3.8+
- **Package Manager**: `uv` (recommended) or `pip`
- **Optional**: Docker & Docker Compose
- **System Requirements**: 
  - RAM: Minimum 2GB, Recommended 4GB+
  - Storage: 500MB for dependencies and models
  - OS: Windows, macOS, or Linux

### 🚄 Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ground-shakers/nust-hackathon-ai-diagnosis.git
   cd nust-hackathon-ai-diagnosis
   ```

2. **Set up Python environment**
   ```bash
   # Using uv (recommended - faster)
   uv venv
   uv pip install -r requirements.txt
   
   # OR using traditional pip
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

3. **Verify data files**
   Ensure these files exist in your project:
   ```
   data/
   ├── training.csv      # ML training dataset
   ├── testing.csv       # ML testing dataset
   └── dataset.csv       # Complete dataset
   
   master-data/
   ├── symptom_severity.csv     # Symptom severity scores
   ├── symptom_description.csv  # Disease descriptions
   └── symptom_precaution.csv   # Medical precautions
   ```

4. **Configure environment (optional)**
   ```bash
   # Copy and customize environment variables
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/macOS
   ```

5. **Start the development server**
   ```bash
   # Method 1: Using the startup script (recommended)
   python run_api.py
   
   # Method 2: Direct uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Method 3: With custom configuration
   set LOG_LEVEL=debug && python run_api.py  # Windows
   # LOG_LEVEL=debug python run_api.py  # Linux/macOS
   ```

6. **Verify installation**
   - 🏠 **API Home**: http://localhost:8000
   - 📚 **Interactive Docs**: http://localhost:8000/docs
   - 📖 **ReDoc**: http://localhost:8000/redoc
   - ❤️ **Health Check**: http://localhost:8000/health

### 🐳 Docker Deployment (Production Ready)

#### Option 1: Docker Compose (Recommended)

```bash
# Start the complete stack (API + Redis)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop the stack
docker-compose down
```

#### Option 2: Manual Docker Setup

1. **Start Redis container**
   ```bash
   docker run -d --name healthcare-redis \
     -p 6379:6379 \
     redis:7-alpine
   ```

2. **Build the API image**
   ```bash
   docker build -t healthcare-diagnosis-api .
   ```

3. **Run the API container**
   ```bash
   docker run -d --name healthcare-api \
     -p 8000:8000 \
     -e REDIS_URL=redis://localhost:6379/0 \
     -v "%cd%\data":/app/data \
     -v "%cd%\master-data":/app/master-data \
     healthcare-diagnosis-api
   ```

#### Environment Configuration

Create a `.env` file for configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# Data Paths
DATA_PATH=data/
MASTER_DATA_PATH=master-data/

# External API
EXTERNAL_API_URL=https://ground-shakers.xyz/api/v1

# Security
ALLOWED_ORIGINS=*
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
```

## 📊 Usage Examples & API Testing

### 🔍 Symptom Search

**Search for symptoms with fuzzy matching:**

```bash
curl -X POST "http://localhost:8000/symptoms/search" \
     -H "Content-Type: application/json" \
     -d '{"symptom": "fever"}'
```

**Response:**
```json
{
  "matches": ["fever", "high_fever", "low_fever"],
  "exact_match": true
}
```

### 🧠 Get Medical Diagnosis

**Complete diagnosis request:**

```bash
curl -X POST "http://localhost:8000/diagnosis" \
     -H "Content-Type: application/json" \
     -d '{
       "initial_symptom": "fever",
       "days_experiencing": 3,
       "additional_symptoms": ["headache", "cough"],
       "user_id": "user_123"
     }'
```

**Response:**
```json
{
  "message": "Diagnosis completed and saved successfully",
  "diagnosis": {
    "id": "diag_abc123",
    "primary_diagnosis": "Common Cold",
    "secondary_diagnosis": "Viral Infection",
    "confidence_level": "High",
    "description": "A viral upper respiratory tract infection...",
    "precautions": [
      "Get adequate rest",
      "Stay hydrated",
      "Take over-the-counter pain relievers if needed"
    ],
    "severity_assessment": "Mild",
    "diagnosed_user_id": "user_123",
    "initial_symptom": "fever",
    "additional_symptoms": ["headache", "cough"],
    "days_experiencing": 3
  }
}
```

### 📈 System Health & Metrics

```bash
# Basic health check
curl -X GET "http://localhost:8000/health"

# Detailed system status
curl -X GET "http://localhost:8000/status"

# Get system statistics
curl -X GET "http://localhost:8000/statistics"
```

### 💡 Advanced Usage Examples

**Get symptom suggestions:**
```bash
curl -X GET "http://localhost:8000/symptoms/suggestions/head?limit=5"
```

**List all symptoms:**
```bash
curl -X GET "http://localhost:8000/symptoms/list"
```

**List all diseases:**
```bash
curl -X GET "http://localhost:8000/diseases/list"
```

**Admin: Reload models:**
```bash
curl -X POST "http://localhost:8000/admin/reload-models"
```

## ⚙️ Configuration & Data Requirements

### Environment Variables

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `HOST` | `0.0.0.0` | Server bind address | `127.0.0.1` |
| `PORT` | `8000` | Server port | `8080` |
| `LOG_LEVEL` | `info` | Logging verbosity | `debug`, `error` |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string | `redis://redis:6379/1` |
| `DATA_PATH` | `data/` | Training data directory | `/app/data/` |
| `MASTER_DATA_PATH` | `master-data/` | Master data directory | `/app/master-data/` |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins | `http://localhost:3000` |
| `EXTERNAL_API_URL` | - | External diagnosis API | `https://api.example.com` |

### 📁 Data File Structure & Requirements

The system requires specific CSV files with defined schemas:

#### Training Data (`data/` directory)
```
data/
├── training.csv     # Primary ML training dataset
├── testing.csv      # Model validation dataset  
└── dataset.csv      # Complete combined dataset
```

**training.csv Schema:**
- **Columns**: Symptom columns (132+) + `prognosis` (target)
- **Format**: Binary encoding (0/1) for symptom presence
- **Size**: ~4,920 rows recommended
- **Example**: `itching,skin_rash,nodal_skin_eruptions,...,prognosis`

#### Master Data (`master-data/` directory)
```
master-data/
├── symptom_severity.csv      # Symptom severity mappings
├── symptom_description.csv   # Disease descriptions
└── symptom_precaution.csv    # Medical precautions
```

**symptom_severity.csv Schema:**
```csv
Symptom,weight
itching,1
skin_rash,3
high_fever,6
```

**symptom_description.csv Schema:**
```csv
Disease,Description
Fungal infection,"A fungal infection is a disease caused by fungus..."
Allergy,"An allergy is a hypersensitive disorder..."
```

**symptom_precaution.csv Schema:**
```csv
Disease,Precaution_1,Precaution_2,Precaution_3,Precaution_4
Fungal infection,"bath twice","use detol or neem in bathing water","keep infected area dry","use clean cloths"
```

## 🔒 Security & Best Practices

### Security Features
- **🛡️ Input Validation**: Comprehensive Pydantic model validation with type safety
- **🔐 Rate Limiting**: Redis-backed rate limiting (60 requests/minute default)
- **🚫 Error Sanitization**: No sensitive information exposed in error responses
- **🌐 CORS Protection**: Configurable cross-origin resource sharing
- **🔑 Idempotency**: Request idempotency with Redis-backed duplicate detection
- **📝 Audit Logging**: Comprehensive request/response logging for monitoring

### Production Security Checklist
```bash
# Environment Variables
- [ ] Set specific ALLOWED_ORIGINS (not *)
- [ ] Use strong Redis passwords
- [ ] Configure LOG_LEVEL=error for production
- [ ] Set up HTTPS/TLS termination
- [ ] Enable request rate limiting

# Infrastructure
- [ ] Deploy behind reverse proxy (nginx/traefik)
- [ ] Use Docker secrets for sensitive data
- [ ] Implement network segmentation
- [ ] Set up monitoring and alerting
```

## 📈 Performance & Monitoring

### Performance Metrics
- **⚡ Response Time**: < 200ms average for symptom search
- **🧠 Diagnosis Time**: < 500ms for complete diagnosis
- **💾 Memory Usage**: ~150MB baseline + model data
- **🔄 Throughput**: 100+ concurrent requests supported

### Monitoring Endpoints
| Endpoint | Purpose | Key Metrics |
|----------|---------|------------|
| `/health` | Service health | Model loading status, Redis connectivity |
| `/status` | System status | Memory usage, request counts, error rates |
| `/statistics` | ML metrics | Model accuracy, prediction confidence, feature importance |

### Logging & Observability
```python
# Log Levels Available
DEBUG    # Detailed diagnosis steps, model predictions
INFO     # Request/response, model loading, API calls  
WARNING  # Invalid symptoms, model fallbacks
ERROR    # API failures, model errors, validation failures
CRITICAL # System failures, startup errors
```

### Scaling Considerations
- **Horizontal Scaling**: Stateless design supports multiple replicas
- **Caching Strategy**: Redis caching for frequently accessed data
- **Load Balancing**: Health check endpoints for load balancer integration
- **Resource Requirements**: 2GB RAM minimum, 4GB+ recommended

## 🧠 Machine Learning Model Details

### Model Architecture
```
Input Layer (132 symptoms)
    ↓
Feature Processing
    ↓
┌─────────────────┐  ┌─────────────────┐
│  Decision Tree  │  │      SVM        │
│   Classifier    │  │   Classifier    │
│                 │  │                 │
│ • Primary Diag  │  │ • Secondary     │
│ • Fast inference│  │ • High accuracy │
│ • Explainable   │  │ • Multi-class   │
└─────────────────┘  └─────────────────┘
    ↓                     ↓
Ensemble Prediction & Confidence Scoring
    ↓
Final Diagnosis + Recommendations
```

### Model Performance
- **Training Accuracy**: ~95%
- **Validation Accuracy**: ~92%
- **Disease Classes**: 41 medical conditions
- **Feature Count**: 132 symptom features
- **Model Size**: ~2MB total

### Supported Medical Conditions
```
Infectious Diseases: Malaria, Dengue, Typhoid, Hepatitis A-E
Allergic Conditions: Allergy, Drug Reaction, Peptic Ulcer Disease
Chronic Diseases: Diabetes, Hypertension, Arthritis, Osteoarthritis
Respiratory: Bronchial Asthma, Pneumonia, Common Cold, COPD
Neurological: Migraine, Cervical Spondylosis, Paralysis (brain hemorrhage)
And 22+ additional conditions...
```

## 🤝 Contributing & Development

### Development Setup
```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/nust-hackathon-ai-diagnosis.git
cd nust-hackathon-ai-diagnosis

# 2. Set up development environment
uv venv
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt  # Development dependencies

# 3. Set up pre-commit hooks
pre-commit install

# 4. Run tests
pytest tests/ -v --cov=src/

# 5. Start development server
python run_api.py
```

### Code Quality Standards

**Required Tools:**
```bash
# Install development dependencies
uv pip install black isort flake8 mypy pytest pytest-cov pre-commit

# Format code
black .
isort .

# Type checking
mypy src/

# Linting
flake8 src/ --max-line-length=88

# Testing
pytest tests/ --cov=src/ --cov-report=html
```

**Code Style Guidelines:**
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for all public functions
- **Line Length**: 88 characters maximum
- **Import Organization**: Sorted with isort

### Contribution Workflow
1. **🍴 Fork** the repository
2. **🌿 Branch** from main (`git checkout -b feature/awesome-feature`)
3. **💻 Develop** with tests and documentation
4. **🧪 Test** your changes (`pytest`)
5. **📝 Document** new features in README
6. **🔍 Review** code quality checks pass
7. **📤 Submit** pull request with detailed description

### Testing Strategy
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Performance tests
pytest tests/performance/ -v --benchmark-only

# Coverage report
pytest --cov=src/ --cov-report=html
```

## 🐛 Troubleshooting & FAQ

### Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Models not loading** | `503 Service Unavailable` | ✅ Verify data files exist<br>✅ Check file permissions<br>✅ Review startup logs |
| **Redis connection failed** | `ConnectionError: Multiple exceptions` | ✅ Start Redis server<br>✅ Check REDIS_URL configuration<br>✅ Verify network connectivity |
| **Port already in use** | `OSError: [Errno 48] Address already in use` | ✅ Change PORT environment variable<br>✅ Kill existing process<br>✅ Use different port |
| **Import/Module errors** | `ModuleNotFoundError` | ✅ Install dependencies: `uv pip install -r requirements.txt`<br>✅ Activate virtual environment |
| **Data format errors** | `KeyError`, `ValueError` during startup | ✅ Verify CSV file schemas<br>✅ Check column names match expected format |
| **Memory errors** | `MemoryError` during model loading | ✅ Increase available RAM<br>✅ Reduce model size<br>✅ Check system resources |

### Debug & Diagnostic Commands

```bash
# Enable debug logging
set LOG_LEVEL=debug && python run_api.py  # Windows
# LOG_LEVEL=debug python run_api.py       # Linux/macOS

# Check system status
curl http://localhost:8000/status | python -m json.tool

# Validate data files
python -c "import pandas as pd; print(pd.read_csv('data/training.csv').shape)"

# Test Redis connection
redis-cli ping

# Check model loading
python -c "from services.model import load_models_and_data; print(load_models_and_data('data/', 'master-data/'))"

# View application logs
tail -f healthcare_api.log  # Linux/macOS
# type healthcare_api.log   # Windows
```

### Performance Optimization

```bash
# Monitor resource usage
docker stats healthcare-api  # If using Docker

# Profile API performance  
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health

# Check model prediction time
time curl -X POST "http://localhost:8000/diagnosis" \
  -H "Content-Type: application/json" \
  -d '{"initial_symptom":"fever","days_experiencing":1,"user_id":"test"}'
```

### FAQ

**Q: How accurate is the diagnosis system?**
A: The system achieves ~92% validation accuracy on test data. However, it's designed for educational purposes and should not replace professional medical consultation.

**Q: Can I add new symptoms or diseases?**
A: Yes, but it requires retraining the models. Add new data to the CSV files and retrain using the provided ML pipeline.

**Q: How do I scale for production?**
A: Use Docker Compose, implement load balancing, add monitoring (Prometheus/Grafana), and consider using managed Redis (AWS ElastiCache, etc.).

**Q: What's the API rate limit?**
A: Default is 60 requests per minute per IP. Configurable via environment variables.

**Q: How do I backup the data?**
A: The CSV files contain all training data. For runtime data, backup Redis if you're storing cache/sessions.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This API is for educational and research purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## 🙋 Support

For questions, issues, or contributions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details

---

**Built by the Ground Shakers using FastAPI, scikit-learn, and modern Python practices**