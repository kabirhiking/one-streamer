"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoBase(BaseModel):
    """Base video schema."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = ""
    visibility: str = Field(default="public", pattern="^(public|unlisted|private)$")


class VideoCreate(VideoBase):
    """Schema for creating a video."""
    pass


class VideoUpdate(BaseModel):
    """Schema for updating a video."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    visibility: Optional[str] = Field(None, pattern="^(public|unlisted|private)$")


class VideoFile(BaseModel):
    """Video file schema."""
    quality: str
    playlist_url: str
    file_size: int
    bitrate: int
    
    class Config:
        from_attributes = True


class VideoResponse(VideoBase):
    """Schema for video response."""
    id: int
    creator_id: int
    thumbnail: Optional[str] = None
    duration: int = 0
    file_size: int = 0
    status: str
    views_count: int = 0
    likes_count: int = 0
    dislikes_count: int = 0
    comments_count: int = 0
    hls_master_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Schema for paginated video list."""
    total: int
    page: int
    page_size: int
    videos: List[VideoResponse]


class UploadResponse(BaseModel):
    """Schema for upload response."""
    video_id: int
    task_id: str
    message: str


class StreamingToken(BaseModel):
    """Schema for streaming token."""
    token: str
    expires_at: datetime
    hls_url: str


class WatchProgress(BaseModel):
    """Schema for watch progress update."""
    video_id: int
    watch_time: int
    completed: bool = False


class AnalyticsResponse(BaseModel):
    """Schema for video analytics."""
    video_id: int
    total_views: int
    total_watch_time: int
    avg_watch_duration: int
    completion_rate: float
    likes: int
    dislikes: int
    comments: int
