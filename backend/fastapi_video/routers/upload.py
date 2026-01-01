"""
Video upload router.
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
import aiofiles
import os
import io
from datetime import datetime

from database import get_db, VideoModel
from schemas import UploadResponse
from auth import get_current_user
from config import settings
from celery_tasks import process_video_task
from storage import upload_file

router = APIRouter()


@router.post("/", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    visibility: str = Form("public"),
    thumbnail: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Upload video file and start processing."""
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_formats_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed formats: {', '.join(settings.allowed_formats_list)}"
        )
    
    # Create video record in database
    video = VideoModel(
        title=title,
        description=description,
        creator_id=user_id,
        status='processing',
        visibility=visibility,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Handle thumbnail upload if provided
    if thumbnail and thumbnail.filename:
        thumbnail_extension = thumbnail.filename.split('.')[-1].lower()
        if thumbnail_extension in ['jpg', 'jpeg', 'png', 'webp']:
            thumbnail_filename = f"video_{video.id}_thumb.{thumbnail_extension}"
            
            try:
                # Read thumbnail content
                thumb_content = await thumbnail.read()
                thumb_bytes = io.BytesIO(thumb_content)
                
                # Determine content type
                content_types = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'webp': 'image/webp'
                }
                content_type = content_types.get(thumbnail_extension, 'image/jpeg')
                
                # Upload to MinIO
                object_name = f"thumbnails/{thumbnail_filename}"
                if upload_file(object_name, thumb_bytes, content_type):
                    # Store relative path in database
                    video.thumbnail = object_name
                    db.commit()
                else:
                    print(f"Failed to upload thumbnail to MinIO")
            except Exception as e:
                print(f"Failed to save thumbnail: {str(e)}")
    
    # Save uploaded file temporarily
    temp_file_path = os.path.join(
        settings.UPLOAD_TEMP_DIR,
        f"{video.id}_{file.filename}"
    )
    
    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        file_size = os.path.getsize(temp_file_path)
        
        # Check file size
        if file_size > settings.MAX_VIDEO_SIZE_MB * 1024 * 1024:
            os.remove(temp_file_path)
            db.delete(video)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.MAX_VIDEO_SIZE_MB}MB"
            )
        
        # Update file size
        video.file_size = file_size
        db.commit()
        
        # Start video processing task
        task = process_video_task.delay(video.id, temp_file_path)
        
        return {
            "video_id": video.id,
            "task_id": task.id,
            "message": "Video upload successful. Processing started."
        }
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        db.delete(video)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/status/{video_id}")
async def get_upload_status(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Get video processing status."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "video_id": video.id,
        "status": video.status,
        "title": video.title,
        "created_at": video.created_at
    }
