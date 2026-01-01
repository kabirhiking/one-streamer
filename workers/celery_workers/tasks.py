"""
Celery worker for video processing tasks.
"""
import os
import sys
import subprocess
import shutil
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database models
from database_models import Video, VideoFile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@postgres:5432/video_streaming_db')

# MinIO configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'videos')
MINIO_USE_SSL = os.getenv('MINIO_USE_SSL', 'False') == 'True'

# Video encoding configuration
QUALITY_LEVELS = {
    '360p': {'resolution': '640x360', 'bitrate': '800k', 'audio_bitrate': '96k'},
    '480p': {'resolution': '854x480', 'bitrate': '1400k', 'audio_bitrate': '128k'},
    '720p': {'resolution': '1280x720', 'bitrate': '2800k', 'audio_bitrate': '128k'},
    '1080p': {'resolution': '1920x1080', 'bitrate': '5000k', 'audio_bitrate': '192k'},
}

SEGMENT_DURATION = int(os.getenv('VIDEO_SEGMENT_DURATION', 10))

# Initialize Celery
app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Initialize database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_SSL
)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_video_info(file_path):
    """Get video information using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        return int(duration)
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return 0


def encode_video_quality(input_path, output_dir, quality):
    """Encode video to specific quality using FFmpeg."""
    config = QUALITY_LEVELS[quality]
    output_path = os.path.join(output_dir, quality)
    os.makedirs(output_path, exist_ok=True)
    
    playlist_file = os.path.join(output_path, 'playlist.m3u8')
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', f"scale={config['resolution']}",
        '-c:v', 'libx264',
        '-b:v', config['bitrate'],
        '-c:a', 'aac',
        '-b:a', config['audio_bitrate'],
        '-hls_time', str(SEGMENT_DURATION),
        '-hls_list_size', '0',
        '-hls_segment_filename', os.path.join(output_path, 'segment_%03d.ts'),
        '-f', 'hls',
        playlist_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return playlist_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error encoding {quality}: {e.stderr.decode()}")
        return None


def create_master_playlist(output_dir, qualities):
    """Create HLS master playlist."""
    master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n\n"
    
    bitrate_map = {
        '360p': 800000,
        '480p': 1400000,
        '720p': 2800000,
        '1080p': 5000000,
    }
    
    for quality in qualities:
        config = QUALITY_LEVELS[quality]
        resolution = config['resolution']
        bitrate = bitrate_map.get(quality, 800000)
        
        master_playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={resolution}\n"
        master_playlist += f"{quality}/playlist.m3u8\n\n"
    
    master_path = os.path.join(output_dir, 'master.m3u8')
    with open(master_path, 'w') as f:
        f.write(master_playlist)
    
    return master_path


def upload_to_minio(local_dir, video_id):
    """Upload processed video files to MinIO."""
    try:
        # Ensure bucket exists
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)
        
        uploaded_files = []
        
        # Upload all files in directory
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                object_name = f"videos/{video_id}/{relative_path}"
                
                # Determine content type
                content_type = 'application/x-mpegURL' if file.endswith('.m3u8') else 'video/MP2T'
                
                minio_client.fput_object(
                    MINIO_BUCKET_NAME,
                    object_name,
                    local_path,
                    content_type=content_type
                )
                
                uploaded_files.append(object_name)
                logger.info(f"Uploaded: {object_name}")
        
        return uploaded_files
    
    except S3Error as e:
        logger.error(f"MinIO upload error: {e}")
        return []


def generate_thumbnail(input_path, video_id):
    """Generate video thumbnail."""
    thumbnail_path = f"/tmp/videos/thumbnail_{video_id}.jpg"
    
    # Get video duration first
    duration = get_video_info(input_path)
    
    # Use 10% of duration or 2 seconds, whichever is smaller
    thumb_time = min(max(duration * 0.1, 2), duration - 1) if duration > 2 else 1
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-ss', str(thumb_time),
        '-vframes', '1',
        '-vf', 'scale=1280:720',
        '-q:v', '2',  # High quality
        thumbnail_path
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, stderr=subprocess.PIPE)
        logger.info(f"Thumbnail generated for video {video_id} at {thumb_time}s")
        
        # Upload thumbnail to MinIO
        object_name = f"thumbnails/{video_id}.jpg"
        minio_client.fput_object(
            MINIO_BUCKET_NAME,
            object_name,
            thumbnail_path,
            content_type='image/jpeg'
        )
        
        logger.info(f"Thumbnail uploaded to MinIO: {object_name}")
        
        # Clean up local thumbnail
        os.remove(thumbnail_path)
        
        return object_name
    
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error generating thumbnail: {e.stderr.decode()}")
        return None
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return None


@app.task(name='tasks.process_video', bind=True)
def process_video(self, video_id, input_file_path):
    """
    Main task to process uploaded video:
    1. Get video information
    2. Encode to multiple qualities (HLS)
    3. Generate thumbnail
    4. Upload to MinIO
    5. Update database
    """
    db = SessionLocal()
    
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"Video {video_id} not found in database")
            return {"status": "error", "message": "Video not found"}
        
        logger.info(f"Processing video {video_id}: {video.title}")
        
        # Get video duration
        duration = get_video_info(input_file_path)
        video.duration = duration
        db.commit()
        
        # Create output directory
        output_dir = f"/tmp/videos/processed_{video_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Encode to different qualities
        encoded_qualities = []
        for quality in ['360p', '480p', '720p', '1080p']:
            logger.info(f"Encoding {quality}...")
            self.update_state(state='PROGRESS', meta={'quality': quality, 'progress': 25})
            
            playlist = encode_video_quality(input_file_path, output_dir, quality)
            if playlist:
                encoded_qualities.append(quality)
                logger.info(f"Successfully encoded {quality}")
        
        if not encoded_qualities:
            raise Exception("Failed to encode any quality levels")
        
        # Create master playlist
        logger.info("Creating master playlist...")
        master_playlist = create_master_playlist(output_dir, encoded_qualities)
        
        # Generate thumbnail
        logger.info("Generating thumbnail...")
        self.update_state(state='PROGRESS', meta={'stage': 'thumbnail', 'progress': 75})
        thumbnail_url = generate_thumbnail(input_file_path, video_id)
        
        # Upload to MinIO
        logger.info("Uploading to storage...")
        self.update_state(state='PROGRESS', meta={'stage': 'upload', 'progress': 85})
        uploaded_files = upload_to_minio(output_dir, video_id)
        
        if not uploaded_files:
            raise Exception("Failed to upload files to storage")
        
        # Update video in database
        video.status = 'ready'
        video.hls_master_url = f"videos/{video_id}/master.m3u8"
        if thumbnail_url:
            video.thumbnail = thumbnail_url
        video.published_at = datetime.utcnow()
        
        # Create video file records
        for quality in encoded_qualities:
            video_file = VideoFile(
                video_id=video_id,
                quality=quality,
                playlist_url=f"videos/{video_id}/{quality}/playlist.m3u8",
                bitrate=int(QUALITY_LEVELS[quality]['bitrate'].replace('k', ''))
            )
            db.add(video_file)
        
        db.commit()
        
        # Clean up temporary files
        logger.info("Cleaning up...")
        os.remove(input_file_path)
        shutil.rmtree(output_dir, ignore_errors=True)
        
        logger.info(f"Video {video_id} processed successfully")
        
        return {
            "status": "success",
            "video_id": video_id,
            "qualities": encoded_qualities,
            "master_playlist": video.hls_master_url
        }
    
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        
        # Update video status to failed
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = 'failed'
                db.commit()
        except:
            pass
        
        # Clean up
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@app.task(name='tasks.cleanup_old_files')
def cleanup_old_files():
    """Periodic task to clean up old temporary files."""
    temp_dir = '/tmp/videos'
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    # Delete files older than 24 hours
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_age.total_seconds() > 86400:  # 24 hours
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {filename}")
            except Exception as e:
                logger.error(f"Error deleting {filename}: {e}")
