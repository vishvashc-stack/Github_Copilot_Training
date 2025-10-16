# Recommendation Microservice

A FastAPI-based microservice for handling product recommendation functionality with MongoDB integration.

## 🚀 Features

- **RESTful API**: Built with FastAPI for high performance and automatic API documentation
- **MongoDB Integration**: Uses PyMongo and Motor for asynchronous database operations
- **Recommendation Engine**: Provides endpoints for generating and managing product recommendations
- **Data Validation**: Comprehensive input validation using Pydantic models
- **Health Monitoring**: Built-in health check endpoints
- **Testing Suite**: Comprehensive unit tests with pytest
- **Async Support**: Full asynchronous request handling for optimal performance

## 📋 Project Structure

```
recommendation_service/
├── app/                          # Main application code
│   ├── __init__.py              # App package initialization
│   ├── main.py                  # FastAPI entrypoint and application setup
│   ├── db.py                    # MongoDB connection and configuration
│   └── routes/                  # API route definitions
│       ├── __init__.py          # Routes package initialization  
│       └── recommendation.py    # Recommendation API endpoints
├── tests/                       # Unit and integration tests
│   ├── __init__.py              # Tests package initialization
│   └── test_recommendation.py   # Recommendation API tests
├── .github/                     # GitHub configuration
│   └── copilot-instructions.md  # Copilot workspace instructions
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation (this file)
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **PyMongo**: Official MongoDB driver for Python
- **Motor**: Async MongoDB driver built on top of PyMongo
- **Pydantic**: Data validation and settings management using Python type hints
- **Uvicorn**: ASGI web server implementation for Python
- **Pytest**: Testing framework for Python applications

## 📦 Installation

### Prerequisites

- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- pip (Python package installer)

### Setup Steps

1. **Clone the repository** (if using version control):
   ```bash
   git clone <repository-url>
   cd recommendation_service
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   Create a `.env` file in the root directory:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=recommendation_db
   ```

5. **Start MongoDB** (if running locally):
   ```bash
   mongod
   ```

## 🚀 Running the Application

### Development Mode

```bash
# From the project root directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health Check
- `GET /health` - Check service health status
- `GET /` - Root endpoint with service information

### Recommendations
- `GET /api/v1/recommendations/{user_id}` - Get recommendations for a specific user
- `POST /api/v1/recommendations/generate` - Generate new recommendations for a user
- `GET /api/v1/recommendations` - Get all recommendations with pagination
- `DELETE /api/v1/recommendations/{recommendation_id}` - Delete a specific recommendation

### Request/Response Examples

#### Generate Recommendations
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "507f1f77bcf86cd799439011",
       "limit": 10,
       "category": "electronics"
     }'
```

#### Get User Recommendations
```bash
curl "http://localhost:8000/api/v1/recommendations/user123?limit=5&category=books"
```

## 🧪 Testing

Run the test suite using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_recommendation.py

# Run with verbose output
pytest -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Name of the MongoDB database | `recommendation_db` |

### MongoDB Collections

The application uses the following MongoDB collections:
- `recommendations` - Stores recommendation data
- `users` - User information and preferences  
- `products` - Product catalog data

## 🐳 Docker Support (Optional)

Create a `Dockerfile` for containerization:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write descriptive docstrings for all functions and classes
- Keep functions focused and single-purpose

### Testing
- Write unit tests for all API endpoints
- Use mocking for database operations in unit tests
- Maintain high test coverage (>80%)
- Include both positive and negative test cases

### Error Handling
- Use appropriate HTTP status codes
- Provide meaningful error messages
- Log errors for debugging purposes
- Handle database connection failures gracefully

## 🔒 Security Considerations

- Add authentication and authorization mechanisms
- Validate and sanitize all input data
- Use environment variables for sensitive configuration
- Implement rate limiting for API endpoints
- Set up CORS policies appropriately

## 🚀 Deployment

### Production Checklist
- [ ] Set up production MongoDB instance
- [ ] Configure environment variables
- [ ] Set up logging and monitoring
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL/TLS certificates
- [ ] Configure health checks and auto-restart
- [ ] Set up backup strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review [PyMongo documentation](https://pymongo.readthedocs.io/)
- Open an issue in the project repository

## 🔄 Changelog

### Version 1.0.0
- Initial release with basic recommendation functionality
- FastAPI integration with automatic API documentation
- MongoDB integration with async support
- Comprehensive test suite
- Health check endpoints