"""
FormatLab Studio - FastAPI Backend
Professional visual generation and editing for FIBO
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import health, analyze, translate, generate, export
from app.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="FormatLab Studio",
    description="Professional JSON-driven visual generation and editing",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/v1")
app.include_router(analyze.router, prefix="/v1")
app.include_router(translate.router, prefix="/v1")
app.include_router(generate.router, prefix="/v1")
app.include_router(export.router, prefix="/v1")

# Static files for outputs (if needed)
os.makedirs("./outputs", exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "app": "FormatLab Studio",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
