from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import AccountSettings, PrivacySettings, ProfileCustomization, Block


@admin.register(AccountSettings)
class AccountSettingsAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'password_changed_at', 'last_updated')
    list_filter = ('password_changed_at',)
    search_fields = ('user__username', 'user__handle', 'user__email')
    readonly_fields = ('user', 'password_changed_at')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Password Information', {
            'fields': ('password_changed_at',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.user.display_name, obj.user.handle)
    user_link.short_description = 'User'
    
    def last_updated(self, obj):
        return obj.password_changed_at.strftime('%Y-%m-%d %H:%M') if obj.password_changed_at else '—'
    last_updated.short_description = 'Password Last Changed'


@admin.register(PrivacySettings)
class PrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'profile_visibility_badge', 'friends_visibility_badge')
    list_filter = ('profile_visibility', 'friends_visibility')
    search_fields = ('user__username', 'user__handle', 'user__email')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'friends_visibility')
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.user.display_name, obj.user.handle)
    user_link.short_description = 'User'
    
    def profile_visibility_badge(self, obj):
        colors = {'public': '#28a745', 'friends': '#ffc107', 'private': '#dc3545'}
        color = colors.get(obj.profile_visibility, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_profile_visibility_display()
        )
    profile_visibility_badge.short_description = 'Profile'
    
    def friends_visibility_badge(self, obj):
        colors = {'public': '#28a745', 'friends': '#ffc107', 'private': '#dc3545'}
        color = colors.get(obj.friends_visibility, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_friends_visibility_display()
        )
    friends_visibility_badge.short_description = 'Friends List'


@admin.register(ProfileCustomization)
class ProfileCustomizationAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'wall_style_badge', 'bio_preview', 'updated_at')
    list_filter = ('wall_style', 'updated_at')
    search_fields = ('user__username', 'user__handle', 'user__email', 'custom_bio')
    readonly_fields = ('user', 'updated_at', 'cover_preview')
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Customization', {
            'fields': ('wall_style', 'custom_bio', 'cover_image', 'cover_preview')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.user.display_name, obj.user.handle)
    user_link.short_description = 'User'
    
    def wall_style_badge(self, obj):
        colors = {'default': '#007bff', 'compact': '#6f42c1', 'detailed': '#28a745'}
        color = colors.get(obj.wall_style, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_wall_style_display()
        )
    wall_style_badge.short_description = 'Wall Style'
    
    def bio_preview(self, obj):
        user_bio = obj.user.bio if hasattr(obj.user, 'bio') and obj.user.bio else None
        if user_bio:
            preview = user_bio[:50] if len(user_bio) > 50 else user_bio
            if len(user_bio) > 50:
                preview += '...'
            return preview
        return '—'
    bio_preview.short_description = 'Bio'
    
    def cover_preview(self, obj):
        if obj.cover_image and obj.cover_image.name:
            return format_html('<img src="{}" width="300" style="max-height: 200px; border-radius: 4px;"/>', obj.cover_image.url)
        return 'No cover image'
    cover_preview.short_description = 'Cover Image Preview'


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker_link', 'blocked_user_link', 'created_at', 'status')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked_user__username', 'blocker__handle', 'blocked_user__handle')
    readonly_fields = ('created_at', 'blocker_info', 'blocked_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Block Information', {
            'fields': ('blocker', 'blocker_info', 'blocked_user', 'blocked_info')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def blocker_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.blocker.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.blocker.display_name, obj.blocker.handle)
    blocker_link.short_description = 'Blocker'
    
    def blocked_user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.blocked_user.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.blocked_user.display_name, obj.blocked_user.handle)
    blocked_user_link.short_description = 'Blocked User'
    
    def status(self, obj):
        return '🚫 Active'
    status.short_description = 'Status'
    
    def blocker_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.blocker.display_name,
            obj.blocker.handle,
            obj.blocker.email
        )
    blocker_info.short_description = 'Blocker Information'
    
    def blocked_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.blocked_user.display_name,
            obj.blocked_user.handle,
            obj.blocked_user.email
        )
    blocked_info.short_description = 'Blocked User Information'

