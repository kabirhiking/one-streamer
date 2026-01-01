"""
URL configuration for users app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    CreatorListView,
    CreatorDetailView,
    SubscriptionListCreateView,
    SubscriptionDeleteView,
    BecomeCreatorView,
    health_check
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('become-creator/', BecomeCreatorView.as_view(), name='become_creator'),
    
    # Creators
    path('creators/', CreatorListView.as_view(), name='creator_list'),
    path('creators/<int:pk>/', CreatorDetailView.as_view(), name='creator_detail'),
    
    # Subscriptions
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscriptions'),
    path('subscriptions/<int:pk>/', SubscriptionDeleteView.as_view(), name='subscription_delete'),
    
    # Health check
    path('health/', health_check, name='health'),
]
