"""
Views for user authentication and profile management.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .models import User, Subscription
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    CreatorSerializer,
    SubscriptionSerializer
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(APIView):
    """Change user password."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Wrong password.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {'message': 'Password updated successfully.'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatorListView(generics.ListAPIView):
    """List all creators."""
    
    queryset = User.objects.filter(is_creator=True)
    serializer_class = CreatorSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_fields = ['channel_name']
    search_fields = ['channel_name', 'display_name', 'channel_description']
    ordering_fields = ['subscribers_count', 'total_views', 'created_at']
    ordering = ['-subscribers_count']


class CreatorDetailView(generics.RetrieveAPIView):
    """Get creator details."""
    
    queryset = User.objects.filter(is_creator=True)
    serializer_class = CreatorSerializer
    permission_classes = (permissions.AllowAny,)


class SubscriptionListCreateView(generics.ListCreateAPIView):
    """List user subscriptions and create new subscription."""
    
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)


class SubscriptionDeleteView(generics.DestroyAPIView):
    """Unsubscribe from a creator."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
    
    def perform_destroy(self, instance):
        creator = instance.creator
        creator.subscribers_count = max(0, creator.subscribers_count - 1)
        creator.save(update_fields=['subscribers_count'])
        instance.delete()


class BecomeCreatorView(APIView):
    """Enable creator mode for user."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        user = request.user
        if user.is_creator:
            return Response(
                {'message': 'Already a creator.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_creator = True
        user.channel_name = request.data.get('channel_name', user.display_name)
        user.save()
        
        return Response(
            UserProfileSerializer(user).data, 
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
