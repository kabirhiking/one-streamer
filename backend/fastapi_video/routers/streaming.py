"""
Video streaming router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db, VideoModel, WatchHistoryModel
from schemas import StreamingToken, WatchProgress
from auth import get_current_user, create_streaming_token
from config import settings

router = APIRouter()


@router.get("/token/{video_id}", response_model=StreamingToken)
async def get_streaming_token(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Generate streaming token for HLS playback."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check access permissions
    if video.visibility == 'private' and video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if video.status != 'ready':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is not ready for streaming"
        )
    
    # Generate token
    token = create_streaming_token(video_id, user_id)
    expires_at = datetime.utcnow() + timedelta(hours=settings.VIDEO_URL_EXPIRATION_HOURS)
    
    # Build HLS URL
    hls_url = f"{settings.STREAM_URL}/videos/{video_id}/master.m3u8?token={token}"
    
    return {
        "token": token,
        "expires_at": expires_at,
        "hls_url": hls_url
    }


@router.post("/progress")
async def update_watch_progress(
    progress: WatchProgress,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Update user's watch progress."""
    
    # Check if watch history exists
    watch_history = db.query(WatchHistoryModel).filter(
        WatchHistoryModel.user_id == user_id,
        WatchHistoryModel.video_id == progress.video_id
    ).first()
    
    if watch_history:
        # Update existing record
        watch_history.watch_time = progress.watch_time
        watch_history.completed = progress.completed
        watch_history.updated_at = datetime.utcnow()
    else:
        # Create new record
        watch_history = WatchHistoryModel(
            user_id=user_id,
            video_id=progress.video_id,
            watch_time=progress.watch_time,
            completed=progress.completed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(watch_history)
    
    db.commit()
    
    return {"message": "Watch progress updated successfully"}


@router.get("/history")
async def get_watch_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Get user's watch history."""
    history = db.query(WatchHistoryModel).filter(
        WatchHistoryModel.user_id == user_id
    ).order_by(WatchHistoryModel.updated_at.desc()).limit(50).all()
    
    return {"history": history}
