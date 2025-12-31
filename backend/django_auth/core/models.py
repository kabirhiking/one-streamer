"""
Core models for videos, comments, likes, and analytics.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Video(models.Model):
    """Video metadata model."""
    
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
    )
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    
    # Video metadata
    thumbnail = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    file_size = models.BigIntegerField(default=0, help_text='File size in bytes')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    
    # Statistics
    views_count = models.BigIntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    # HLS streaming
    hls_master_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['creator', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['visibility', '-views_count']),
            models.Index(fields=['-published_at']),
        ]
    
    def __str__(self):
        return self.title


class VideoFile(models.Model):
    """Video quality variants and HLS segments."""
    
    QUALITY_CHOICES = (
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    )
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='files')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    playlist_url = models.URLField()  # HLS playlist URL
    file_size = models.BigIntegerField(default=0)
    bitrate = models.IntegerField(default=0, help_text='Bitrate in kbps')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_files'
        unique_together = ('video', 'quality')
        ordering = ['quality']
    
    def __str__(self):
        return f"{self.video.title} - {self.quality}"


class Comment(models.Model):
    """Video comments."""
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    content = models.TextField(max_length=1000)
    likes_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.video.title}"


class Like(models.Model):
    """Video and comment likes/dislikes."""
    
    LIKE_TYPE_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    like_type = models.CharField(max_length=10, choices=LIKE_TYPE_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'video'],
                name='unique_video_like',
                condition=models.Q(video__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_like',
                condition=models.Q(comment__isnull=False)
            ),
        ]
        indexes = [
            models.Index(fields=['video', 'like_type']),
            models.Index(fields=['comment', 'like_type']),
        ]
    
    def __str__(self):
        target = self.video or self.comment
        return f"{self.user.email} {self.like_type}s {target}"


class WatchHistory(models.Model):
    """User watch history."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watch_history'
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watch_time = models.IntegerField(default=0, help_text='Watch time in seconds')
    completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watch_history'
        unique_together = ('user', 'video')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} watched {self.video.title}"


class VideoAnalytics(models.Model):
    """Daily analytics for videos."""
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Metrics
    views = models.IntegerField(default=0)
    watch_time = models.BigIntegerField(default=0, help_text='Total watch time in seconds')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
    # Audience
    unique_viewers = models.IntegerField(default=0)
    avg_watch_duration = models.IntegerField(default=0, help_text='Average watch duration in seconds')
    completion_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_analytics'
        unique_together = ('video', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['video', '-date']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.video.title} on {self.date}"
