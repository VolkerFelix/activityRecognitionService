# Activity Recognition Service

A microservice for analyzing and recognizing activity patterns from acceleration data, built with FastAPI.

## Overview

This service provides APIs for analyzing acceleration data to recognize various physical activities. It's designed to be part of Areum's larger ecosystem of health and activity monitoring services.

## Features

- Activity pattern recognition from acceleration data
- RESTful API endpoints
- Health monitoring
- CORS support
- API documentation (Swagger UI)

## Tech Stack

- FastAPI - Modern web framework for building APIs
- Pydantic - Data validation using Python type annotations
- NumPy & Pandas - Data manipulation and analysis
- Scikit-learn - Machine learning capabilities
- Docker support for containerization

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/activityRecognitionService.git
cd activityRecognitionService
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

## Running the Service

### Local Development

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

### Docker

Build and run using Docker:

```bash
docker build -t activity-recognition-service .
docker run -p 8000:8000 activity-recognition-service
```

## API Documentation

Once the service is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Testing

Run tests using pytest:

```bash
pytest
```

## Project Structure

```
activityRecognitionService/
├── app/
│   ├── api/        # API routes and endpoints
│   ├── core/       # Core configuration and settings
│   ├── models/     # Data models and schemas
│   ├── services/   # Business logic and services
│   └── utils/      # Utility functions
├── tests/          # Test files
├── Dockerfile      # Container configuration
├── requirements.txt # Python dependencies
└── pyproject.toml  # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the terms specified in the LICENSE file.
