"""
Serializers for user authentication and profile management.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Subscription


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'display_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'display_name',
                  'full_name', 'bio', 'avatar', 'is_creator', 'channel_name',
                  'channel_description', 'subscribers_count', 'total_views',
                  'created_at')
        read_only_fields = ('id', 'email', 'subscribers_count', 'total_views', 
                           'created_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'display_name', 'bio', 'avatar',
                  'channel_name', 'channel_description')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class CreatorSerializer(serializers.ModelSerializer):
    """Serializer for creator profile (public view)."""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'display_name', 'full_name', 'channel_name', 
                  'channel_description', 'avatar', 'subscribers_count', 
                  'total_views', 'created_at')
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    
    creator = CreatorSerializer(read_only=True)
    creator_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Subscription
        fields = ('id', 'creator', 'creator_id', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def validate_creator_id(self, value):
        try:
            creator = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Creator not found.")
        
        # Don't allow subscribing to yourself
        if self.context['request'].user.id == value:
            raise serializers.ValidationError("You cannot subscribe to yourself.")
        
        return value
    
    def create(self, validated_data):
        creator_id = validated_data.pop('creator_id')
        creator = User.objects.get(id=creator_id)
        
        # Check if already subscribed - return existing subscription
        existing = Subscription.objects.filter(
            subscriber=self.context['request'].user,
            creator=creator
        ).first()
        
        if existing:
            return existing
        
        subscription = Subscription.objects.create(
            subscriber=self.context['request'].user,
            creator=creator
        )
        # Update subscriber count
        creator.subscribers_count += 1
        creator.save(update_fields=['subscribers_count'])
        return subscription
