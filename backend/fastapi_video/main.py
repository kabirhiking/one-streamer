"""
FastAPI Video Service - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from config import settings
from routers import videos, upload, streaming, analytics
from database import engine, Base

# Don't create tables - Django manages the schema
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Video Streaming Platform - Video Service",
    description="FastAPI service for video upload, processing, and streaming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(streaming.router, prefix="/api/stream", tags=["Streaming"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Streaming Platform - Video Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "video-service"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )
