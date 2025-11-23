from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.config import settings
from src.routes import chat, reasoning, tools
from src.models.schemas import HealthResponse
import os

# Initialize FastAPI app
app = FastAPI(
    title="Nemotron Backend API",
    description="Backend service for NVIDIA Llama-3.3-Nemotron-Super-49B-v1.5 model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(reasoning.router, prefix="/api/v1", tags=["Reasoning"])
app.include_router(tools.router, prefix="/api/v1", tags=["Tools"])

# Mount frontend static files (must be after API routes)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "operational",
        "model": settings.model_name,
        "api_configured": bool(settings.nvidia_api_key)
    }


async def health_check():
    """
    Health check endpoint to verify service status.

    Returns service status, model name, and API configuration status.
    """
    return {
        "status": "operational",
        "model": settings.model_name,
        "api_configured": bool(settings.nvidia_api_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
