"""
Configuration settings for FastAPI application.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Video Streaming Platform - Video Service"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = 'postgresql://postgres:postgres123@postgres:5432/video_streaming_db'
    
    # JWT
    JWT_SECRET_KEY: str = 'your-jwt-secret-key'
    JWT_ALGORITHM: str = 'HS256'
    
    # MinIO
    MINIO_ENDPOINT: str = 'minio:9000'
    MINIO_ACCESS_KEY: str = 'minioadmin'
    MINIO_SECRET_KEY: str = 'minioadmin123'
    MINIO_BUCKET_NAME: str = 'videos'
    MINIO_USE_SSL: bool = False
    
    # Redis
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Celery
    CELERY_BROKER_URL: str = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND: str = 'redis://redis:6379/0'
    
    # Video Processing
    MAX_VIDEO_SIZE_MB: int = 500
    VIDEO_SEGMENT_DURATION: int = 10
    
    # Upload
    UPLOAD_TEMP_DIR: str = '/tmp/videos'
    THUMBNAIL_DIR: str = '/app/media/thumbnails'
    
    # Streaming
    VIDEO_URL_EXPIRATION_HOURS: int = 24
    STREAM_URL: str = 'http://localhost:8080'
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def allowed_formats_list(self) -> List[str]:
        """Get allowed video formats as list."""
        return ['mp4', 'avi', 'mov', 'mkv']
    
    @property
    def quality_levels_list(self) -> List[str]:
        """Get quality levels as list."""
        return ['360p', '480p', '720p', '1080p']
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        return ['http://localhost:3000', 'http://localhost:8000', 'http://localhost:8080']


settings = Settings()
