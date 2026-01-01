from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ('email', 'display_name', 'is_creator', 'subscribers_count', 
                   'is_staff', 'created_at')
    list_filter = ('is_creator', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'display_name', 'channel_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'display_name', 
                                     'bio', 'avatar')}),
        ('Creator info', {'fields': ('is_creator', 'channel_name', 
                                     'channel_description')}),
        ('Statistics', {'fields': ('subscribers_count', 'total_views')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""
    
    list_display = ('subscriber', 'creator', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__email', 'creator__email')
    ordering = ('-created_at',)
    raw_id_fields = ('subscriber', 'creator')
