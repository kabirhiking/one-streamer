"""
Views for core functionality.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import F
from .models import Video, Comment, Like
from .serializers import CommentSerializer, CommentCreateSerializer, LikeSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    """List and create comments for a video."""
    
    permission_classes = [permissions.AllowAny]  # Anyone can view, auth required for POST
    
    def get_queryset(self):
        """Get comments for a specific video (top-level only)."""
        video_id = self.kwargs.get('video_id')
        return Comment.objects.filter(
            video_id=video_id,
            parent__isnull=True
        ).select_related('user').prefetch_related('replies')
    
    def get_serializer_class(self):
        """Use different serializers for GET and POST."""
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """Create a comment."""
        # Check if user is authenticated for POST
        if not self.request.user.is_authenticated:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Authentication required to post comments")
        
        comment = serializer.save(user=self.request.user)
        # Update video comment count
        Video.objects.filter(id=comment.video_id).update(
            comments_count=F('comments_count') + 1
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific comment."""
    
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Only comment owner can update."""
        if serializer.instance.user != self.request.user:
            return Response(
                {'error': 'You can only edit your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only comment owner can delete."""
        if instance.user != self.request.user:
            return Response(
                {'error': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        video_id = instance.video_id
        instance.delete()
        # Update video comment count
        Video.objects.filter(id=video_id).update(
            comments_count=F('comments_count') - 1
        )


class LikeToggleView(generics.GenericAPIView):
    """Toggle like/dislike on video or comment."""
    
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Toggle like/dislike."""
        video_id = request.data.get('video')
        comment_id = request.data.get('comment')
        like_type = request.data.get('like_type', 'like')
        
        if not video_id and not comment_id:
            return Response(
                {'error': 'Either video or comment must be specified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find existing like
        filter_kwargs = {'user': request.user}
        if video_id:
            filter_kwargs['video_id'] = video_id
        else:
            filter_kwargs['comment_id'] = comment_id
        
        existing_like = Like.objects.filter(**filter_kwargs).first()
        
        if existing_like:
            if existing_like.like_type == like_type:
                # Remove like
                existing_like.delete()
                self._update_counts(video_id, comment_id, like_type, -1)
                return Response({'message': 'Like removed'}, status=status.HTTP_200_OK)
            else:
                # Change like type
                old_type = existing_like.like_type
                existing_like.like_type = like_type
                existing_like.save()
                self._update_counts(video_id, comment_id, old_type, -1)
                self._update_counts(video_id, comment_id, like_type, 1)
                return Response({'message': 'Like updated'}, status=status.HTTP_200_OK)
        else:
            # Create new like
            Like.objects.create(
                user=request.user,
                video_id=video_id,
                comment_id=comment_id,
                like_type=like_type
            )
            self._update_counts(video_id, comment_id, like_type, 1)
            return Response({'message': 'Like added'}, status=status.HTTP_201_CREATED)
    
    def _update_counts(self, video_id, comment_id, like_type, delta):
        """Update like/dislike counts."""
        field = 'likes_count' if like_type == 'like' else 'dislikes_count'
        
        if video_id:
            Video.objects.filter(id=video_id).update(**{field: F(field) + delta})
        elif comment_id:
            Comment.objects.filter(id=comment_id).update(**{field: F(field) + delta})

