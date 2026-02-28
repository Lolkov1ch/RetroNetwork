from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Follow

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('handle', 'display_name', 'email', 'status_badge', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'status', 'date_joined')
    search_fields = ('username', 'handle', 'email', 'display_name')
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('display_name', 'handle', 'bio', 'avatar', 'avatar_preview', 'birth_date')
        }),
        ('Status & Activity', {
            'fields': ('status', 'previous_status')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'online': '#28a745',
            'dnd': '#dc3545',
            'inactive': '#ffc107',
            'offline': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def avatar_preview(self, obj):
        if obj.avatar and obj.avatar.name:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;"/>', obj.avatar.url)
        return 'No avatar'
    avatar_preview.short_description = 'Avatar Preview'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower_link', 'following_link', 'created_at', 'status')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username', 'follower__handle', 'following__handle')
    readonly_fields = ('created_at', 'follower_info', 'following_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Follow Information', {
            'fields': ('follower', 'follower_info', 'following', 'following_info')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def follower_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.follower.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.follower.display_name, obj.follower.handle)
    follower_link.short_description = 'Follower'
    
    def following_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.following.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.following.display_name, obj.following.handle)
    following_link.short_description = 'Following'
    
    def status(self, obj):
        return '✓ Active'
    status.short_description = 'Status'
    
    def follower_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.follower.display_name,
            obj.follower.handle,
            obj.follower.email
        )
    follower_info.short_description = 'Follower Information'
    
    def following_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.following.display_name,
            obj.following.handle,
            obj.following.email
        )
    following_info.short_description = 'Following Information'