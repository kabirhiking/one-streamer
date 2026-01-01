#!/usr/bin/env python
"""
Script to regenerate thumbnails for existing videos
"""
import os
import sys
import subprocess
import tempfile
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, '/app')
from database_models import Video

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@postgres:5432/video_streaming_db')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'videos')
MINIO_USE_SSL = os.getenv('MINIO_USE_SSL', 'False').lower() == 'true'

# Initialize
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_SSL
)


def generate_thumbnail_from_segment(video_id):
    """Generate thumbnail from first video segment in MinIO."""
    try:
        # Download first segment from 360p quality
        segment_path = f"videos/{video_id}/360p/segment_000.ts"
        
        print(f"📥 Downloading segment: {segment_path}")
        
        # Create temp file for segment
        temp_segment = tempfile.NamedTemporaryFile(suffix='.ts', delete=False)
        minio_client.fget_object(
            MINIO_BUCKET_NAME,
            segment_path,
            temp_segment.name
        )
        
        # Create temp file for thumbnail
        temp_thumb = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_thumb.close()
        
        print(f"🎨 Generating thumbnail from segment...")
        
        # Extract frame from segment
        cmd = [
            'ffmpeg',
            '-i', temp_segment.name,
            '-ss', '3',  # 3 seconds into segment
            '-vframes', '1',
            '-vf', 'scale=1280:720',
            '-q:v', '2',
            temp_thumb.name,
            '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr.decode()[:200]}")
            return None
        
        # Upload to MinIO
        object_name = f"thumbnails/{video_id}.jpg"
        
        print(f"☁️  Uploading thumbnail to MinIO: {object_name}")
        
        minio_client.fput_object(
            MINIO_BUCKET_NAME,
            object_name,
            temp_thumb.name,
            content_type='image/jpeg'
        )
        
        # Cleanup
        os.unlink(temp_segment.name)
        os.unlink(temp_thumb.name)
        
        print(f"✅ Thumbnail generated successfully!")
        return object_name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Regenerate thumbnails for all ready videos without thumbnails."""
    db = SessionLocal()
    
    try:
        # Get all ready videos without thumbnails
        videos = db.query(Video).filter(
            Video.status == 'ready',
            (Video.thumbnail == None) | (Video.thumbnail == '')
        ).all()
        
        print(f"\n🎬 Found {len(videos)} videos without thumbnails\n")
        
        for video in videos:
            print(f"{'='*60}")
            print(f"Processing Video #{video.id}: {video.title}")
            print(f"{'='*60}")
            
            thumbnail_url = generate_thumbnail_from_segment(video.id)
            
            if thumbnail_url:
                # Update database
                video.thumbnail = thumbnail_url
                db.commit()
                print(f"💾 Database updated with thumbnail URL\n")
            else:
                print(f"⚠️  Failed to generate thumbnail\n")
        
        print(f"\n{'='*60}")
        print(f"✨ Done! Generated {len([v for v in videos if v.thumbnail])} thumbnails")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()
