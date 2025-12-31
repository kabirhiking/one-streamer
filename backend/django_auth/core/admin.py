from django.contrib import admin
from .models import Video, VideoFile, Comment, Like, WatchHistory, VideoAnalytics


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'visibility', 'views_count', 
                   'likes_count', 'created_at')
    list_filter = ('status', 'visibility', 'created_at')
    search_fields = ('title', 'description', 'creator__email')
    ordering = ('-created_at',)
    raw_id_fields = ('creator',)
    readonly_fields = ('views_count', 'likes_count', 'dislikes_count', 
                      'comments_count', 'created_at', 'updated_at')


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('video', 'quality', 'file_size', 'bitrate', 'created_at')
    list_filter = ('quality', 'created_at')
    search_fields = ('video__title',)
    ordering = ('-created_at',)
    raw_id_fields = ('video',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'content_preview', 'likes_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__email', 'video__title')
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'video', 'parent')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'comment', 'like_type', 'created_at')
    list_filter = ('like_type', 'created_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'video', 'comment')


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'watch_time', 'completed', 'updated_at')
    list_filter = ('completed', 'updated_at')
    search_fields = ('user__email', 'video__title')
    ordering = ('-updated_at',)
    raw_id_fields = ('user', 'video')


@admin.register(VideoAnalytics)
class VideoAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('video', 'date', 'views', 'watch_time', 'unique_viewers', 
                   'completion_rate')
    list_filter = ('date',)
    search_fields = ('video__title',)
    ordering = ('-date',)
    raw_id_fields = ('video',)
