"""
Database configuration and models.
"""
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config import settings

# Create database engine - don't check foreign keys since Django manages schema
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database models (read-only for FastAPI, Django manages schema)
class VideoModel(Base):
    """Video model matching Django's Video model."""
    __tablename__ = 'videos'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, nullable=False)  # Foreign key managed by Django
    
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)


class VideoFileModel(Base):
    """Video file model matching Django's VideoFile model."""
    __tablename__ = 'video_files'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False)  # Foreign key managed by Django
    quality = Column(String(10), nullable=False)
    playlist_url = Column(String(200), nullable=False)
    file_size = Column(BigInteger, default=0)
    bitrate = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class WatchHistoryModel(Base):
    """Watch history model."""
    __tablename__ = 'watch_history'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key managed by Django
    video_id = Column(Integer, nullable=False)  # Foreign key managed by Django
    watch_time = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
