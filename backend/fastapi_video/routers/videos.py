"""
Video management router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db, VideoModel
from schemas import VideoResponse, VideoListResponse, VideoCreate, VideoUpdate
from auth import get_current_user

router = APIRouter()


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    creator_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(recent|views|likes)$"),
    db: Session = Depends(get_db)
):
    """List videos with pagination, filters, and search."""
    query = db.query(VideoModel).filter(VideoModel.visibility == 'public')
    
    if creator_id:
        query = query.filter(VideoModel.creator_id == creator_id)
    
    if status:
        query = query.filter(VideoModel.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (VideoModel.title.ilike(search_term)) | 
            (VideoModel.description.ilike(search_term))
        )
    
    total = query.count()
    
    # Apply sorting
    if sort_by == "views":
        query = query.order_by(VideoModel.views_count.desc())
    elif sort_by == "likes":
        query = query.order_by(VideoModel.likes_count.desc())
    else:  # recent or default
        query = query.order_by(VideoModel.created_at.desc())
    
    videos = query.offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "videos": videos
    }


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user)
):
    """Get video by ID."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check visibility
    if video.visibility == 'private' and video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Increment view count
    video.views_count += 1
    db.commit()
    
    return video


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Update video metadata."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this video"
        )
    
    # Update fields
    update_data = video_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)
    
    db.commit()
    db.refresh(video)
    
    return video


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Delete video."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    db.delete(video)
    db.commit()
    
    return {"message": "Video deleted successfully"}


@router.get("/creator/{creator_id}", response_model=VideoListResponse)
async def get_creator_videos(
    creator_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all videos from a creator."""
    query = db.query(VideoModel).filter(
        VideoModel.creator_id == creator_id,
        VideoModel.visibility.in_(['public', 'unlisted'])
    )
    
    total = query.count()
    
    videos = query.order_by(VideoModel.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "videos": videos
    }
