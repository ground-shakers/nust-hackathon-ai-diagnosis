# Healthcare Diagnosis API

An AI-powered healthcare diagnosis system built with FastAPI and scikit-learn that provides intelligent symptom analysis and medical recommendations.

## 🚀 Features

- **Intelligent Symptom Search**: Fuzzy matching for symptom queries
- **AI-Powered Diagnosis**: Machine learning-based medical diagnosis using Decision Trees and SVM
- **Severity Assessment**: Risk evaluation based on symptoms and duration
- **Comprehensive API**: RESTful endpoints with full documentation
- **Robust Error Handling**: Detailed error responses and logging
- **Health Monitoring**: System status and model performance metrics
- **Data Validation**: Input validation with Pydantic models
- **Async Support**: Asynchronous request handling
- **CORS Enabled**: Cross-origin resource sharing support

## 📋 API Endpoints

### Health Check

- `GET /` - Basic health check
- `GET /health` - Detailed health status
- `GET /status` - System status and statistics

### Symptom Management

- `POST /symptoms/search` - Search for symptoms
- `GET /symptoms/suggestions/{partial_symptom}` - Get symptom suggestions
- `GET /symptoms/list` - List all available symptoms

### Diagnosis

- `POST /diagnosis` - Get medical diagnosis
- `GET /diseases/list` - List all diagnosable diseases
- `GET /statistics` - Get system statistics

### Administration

- `POST /admin/reload-models` - Reload ML models

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- uv package manager

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/ground-shakers/nust-hackathon-ai-diagnosis.git
   cd nust-hackathon-ai-diagnosis
   ```

2. **Install dependencies**

   ```bash
   uv pip install -r requirements.txt
   ```

4. **Prepare data files**
   Ensure the following files are present:
   - `data/Training.csv`
   - `data/Testing.csv`
   - `master-data/symptom_severity.csv`
   - `master-data/symptom_Description.csv`
   - `master-data/symptom_precaution.csv`

5. **Start the API**

   ```bash
   python run_api.py
   ```

   Or directly with uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API Documentation: <http://localhost:8000/docs>
   - ReDoc Documentation: <http://localhost:8000/redoc>
   - Health Check: <http://localhost:8000/health>

## 🐳 Docker Deployment

1. **Build the image**

   ```bash
   docker build -t healthcare-diagnosis-api .
   ```

2. **Run the container**

   ```bash
   docker run -d -p 8000:8000 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/master-data:/app/master-data \
     healthcare-diagnosis-api
   ```

## 📊 Usage Examples

### Search for Symptoms

```bash
curl -X POST "http://localhost:8000/symptoms/search" \
     -H "Content-Type: application/json" \
     -d '{"symptom": "fever"}'
```

### Get Diagnosis

```bash
curl -X POST "http://localhost:8000/diagnosis" \
     -H "Content-Type: application/json" \
     -d '{
       "initial_symptom": "fever",
       "days_experiencing": 3,
       "additional_symptoms": ["headache", "cough"]
     }'
```

### Check System Status

```bash
curl -X GET "http://localhost:8000/status"
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `DATA_PATH` | data/ | Path to training data |
| `MASTER_DATA_PATH` | master-data/ | Path to master data |
| `LOG_LEVEL` | info | Logging level |
| `ALLOWED_ORIGINS` | * | CORS allowed origins |

### Data File Requirements

1. **Training.csv**: Medical training data with symptoms and diagnoses
2. **Testing.csv**: Test dataset for model validation
3. **symptom_severity.csv**: Severity scores for symptoms
4. **symptom_Description.csv**: Descriptions for medical conditions
5. **symptom_precaution.csv**: Recommended precautions for conditions

## 🔒 Security Considerations

- Input validation with Pydantic models
- Error handling without sensitive information exposure
- CORS configuration for production environments
- Rate limiting considerations for production deployment
- Secure environment variable management

## 📈 Performance & Monitoring

- Model performance metrics available via `/statistics`
- Comprehensive logging for debugging and monitoring
- Health check endpoints for load balancer integration
- Async request handling for better concurrency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Add docstrings for all functions and classes
- Format code with Black: `black .`
- Sort imports with isort: `isort .`
- Lint with flake8: `flake8 .`

## 🐛 Troubleshooting

### Common Issues

1. **Models not loading**: Check if all data files are present and accessible
2. **Port already in use**: Change the PORT environment variable
3. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
4. **Data file format**: Verify CSV files have the expected column structure

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=debug
python run_api.py
```

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