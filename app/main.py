"""
FastAPI entrypoint and application setup.

This module initializes the FastAPI application and configures
all routes, middleware, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import recommendation
from app.db import connect_to_mongo, close_mongo_connection

# Create FastAPI application instance
app = FastAPI(
    title="Recommendation Microservice",
    description="A microservice for handling product recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendation.router, prefix="/api/v1", tags=["recommendations"])

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on application startup."""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on application shutdown."""
    await close_mongo_connection()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy", "service": "recommendation-microservice"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic service information."""
    return {
        "message": "Welcome to the Recommendation Microservice",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)