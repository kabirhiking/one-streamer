"""
URL configuration for core app.
"""
from django.urls import path
from .views import (
    health_check,
    CommentListCreateView,
    CommentDetailView,
    LikeToggleView
)

urlpatterns = [
    # Health check
    path('health/', health_check, name='core_health'),
    
    # Comments
    path('videos/<int:video_id>/comments/', CommentListCreateView.as_view(), name='video_comments'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    
    # Likes
    path('likes/', LikeToggleView.as_view(), name='like_toggle'),
]
