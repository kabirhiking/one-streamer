"""
Analytics router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import get_db, VideoModel, WatchHistoryModel
from schemas import AnalyticsResponse
from auth import get_current_user

router = APIRouter()


@router.get("/video/{video_id}", response_model=AnalyticsResponse)
async def get_video_analytics(
    video_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Get analytics for a specific video."""
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Only creator can view analytics
    if video.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get watch history stats
    watch_stats = db.query(
        func.count(WatchHistoryModel.id).label('total_watches'),
        func.sum(WatchHistoryModel.watch_time).label('total_watch_time'),
        func.avg(WatchHistoryModel.watch_time).label('avg_watch_time'),
        func.count(WatchHistoryModel.id).filter(WatchHistoryModel.completed == True).label('completions')
    ).filter(WatchHistoryModel.video_id == video_id).first()
    
    total_watch_time = watch_stats.total_watch_time or 0
    avg_watch_duration = int(watch_stats.avg_watch_time or 0)
    completions = watch_stats.completions or 0
    total_watches = watch_stats.total_watches or 1  # Avoid division by zero
    
    completion_rate = (completions / total_watches * 100) if total_watches > 0 else 0
    
    return {
        "video_id": video.id,
        "total_views": video.views_count,
        "total_watch_time": total_watch_time,
        "avg_watch_duration": avg_watch_duration,
        "completion_rate": round(completion_rate, 2),
        "likes": video.likes_count,
        "dislikes": video.dislikes_count,
        "comments": video.comments_count
    }


@router.get("/creator")
async def get_creator_analytics(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """Get overall analytics for creator's channel."""
    
    # Get all creator's videos
    videos = db.query(VideoModel).filter(VideoModel.creator_id == user_id).all()
    
    if not videos:
        return {
            "total_videos": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "videos": []
        }
    
    video_ids = [v.id for v in videos]
    
    # Aggregate stats
    total_views = sum(v.views_count for v in videos)
    total_likes = sum(v.likes_count for v in videos)
    total_comments = sum(v.comments_count for v in videos)
    
    # Get watch time
    total_watch_time = db.query(
        func.sum(WatchHistoryModel.watch_time)
    ).filter(WatchHistoryModel.video_id.in_(video_ids)).scalar() or 0
    
    return {
        "total_videos": len(videos),
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_watch_time": total_watch_time,
        "videos": [
            {
                "id": v.id,
                "title": v.title,
                "views": v.views_count,
                "likes": v.likes_count,
                "created_at": v.created_at
            }
            for v in videos
        ]
    }


@router.get("/trending")
async def get_trending_videos(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get trending videos based on recent views."""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    videos = db.query(VideoModel).filter(
        VideoModel.visibility == 'public',
        VideoModel.status == 'ready',
        VideoModel.created_at >= since_date
    ).order_by(VideoModel.views_count.desc()).limit(20).all()
    
    return {"trending": videos}
