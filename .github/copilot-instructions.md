# Recommendation Microservice - Copilot Instructions

This is a FastAPI-based microservice for handling recommendation functionality with MongoDB integration.

## Project Structure
- `app/` - Main application code
- `app/main.py` - FastAPI entrypoint and application setup
- `app/routes/` - API route definitions
- `app/db.py` - MongoDB database connection and configuration
- `tests/` - Unit and integration tests
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Development Guidelines
- Use FastAPI for REST API development
- Use PyMongo for MongoDB database operations
- Follow Python best practices and PEP 8 style guide
- Write comprehensive tests for all API endpoints
- Use proper error handling and logging
- Implement proper data validation using Pydantic models

## Dependencies
- FastAPI for web framework
- PyMongo for MongoDB integration
- Uvicorn for ASGI server
- Pytest for testing
- Python-dotenv for environment variables