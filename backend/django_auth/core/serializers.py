"""
Serializers for core app.
"""
from rest_framework import serializers
from .models import Video, Comment, Like
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer."""
    
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'video', 'user', 'user_name', 'user_email', 'parent', 
                  'content', 'likes_count', 'created_at', 'updated_at', 'replies')
        read_only_fields = ('id', 'user', 'user_name', 'user_email', 
                           'likes_count', 'created_at', 'updated_at', 'replies')
    
    def get_replies(self, obj):
        """Get comment replies."""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ('video', 'parent', 'content')
    
    def validate(self, data):
        """Validate comment data."""
        if not data.get('content', '').strip():
            raise serializers.ValidationError("Comment content cannot be empty")
        return data


class LikeSerializer(serializers.ModelSerializer):
    """Like/Dislike serializer."""
    
    class Meta:
        model = Like
        fields = ('id', 'user', 'video', 'comment', 'like_type', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
