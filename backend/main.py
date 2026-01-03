"""FastAPI Main Application

This module serves as the entry point for the Ramayana Sustainability Training backend API.
It configures the FastAPI application, CORS middleware, and includes all route modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers (these will be created separately)
# from routes import users, modules, chatbot, analytics

app = FastAPI(
    title="Ramayana Sustainability Training API",
    description="Backend API for the Ramayana-themed sustainability training platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is running.
    
    Returns:
        dict: Status message and API version
    """
    return {
        "status": "healthy",
        "message": "Ramayana Sustainability Training API is running",
        "version": "1.0.0"
    }


# Include routers
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
# app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.on_event("startup")
async def startup_event():
    """Execute tasks on application startup."""
    print("Starting Ramayana Sustainability Training API...")
    # Initialize database tables, connections, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Execute cleanup tasks on application shutdown."""
    print("Shutting down Ramayana Sustainability Training API...")
    # Close database connections, cleanup resources, etc.


if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
