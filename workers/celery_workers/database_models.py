"""
Database models for Celery workers.
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Video(Base):
    """Video model."""
    __tablename__ = 'videos'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, nullable=False)
    
    thumbnail = Column(String(200))
    duration = Column(Integer, default=0)
    file_size = Column(BigInteger, default=0)
    
    status = Column(String(20), default='processing')
    visibility = Column(String(20), default='public')
    
    views_count = Column(BigInteger, default=0)
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    hls_master_url = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)


class VideoFile(Base):
    """Video file model."""
    __tablename__ = 'video_files'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False)  # Foreign key managed by Django
    quality = Column(String(10), nullable=False)
    playlist_url = Column(String(200), nullable=False)
    file_size = Column(BigInteger, default=0)
    bitrate = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
