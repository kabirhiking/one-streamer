"""
User models for video streaming platform.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model."""
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    
    # Profile fields
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Channel fields
    is_creator = models.BooleanField(default=False)
    channel_name = models.CharField(max_length=100, blank=True)
    channel_description = models.TextField(max_length=1000, blank=True)
    
    # Statistics
    subscribers_count = models.IntegerField(default=0)
    total_views = models.BigIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_creator']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return user's full name or display name."""
        return self.display_name or f"{self.first_name} {self.last_name}".strip() or self.email


class Subscription(models.Model):
    """User subscriptions to creators."""
    
    subscriber = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscribers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscriptions'
        unique_together = ('subscriber', 'creator')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscriber', '-created_at']),
            models.Index(fields=['creator', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.subscriber.email} subscribes to {self.creator.email}"
