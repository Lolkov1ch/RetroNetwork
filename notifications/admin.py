from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'type_badge', 'content_preview', 'sender_link', 'read_status', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__handle', 'content', 'sender__username', 'sender__handle')
    readonly_fields = ('created_at', 'user_info', 'sender_info', 'full_content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'user_info', 'type', 'sender', 'sender_info')
        }),
        ('Content', {
            'fields': ('content', 'full_content')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{} (@{})</a>',
            url,
            obj.user.display_name,
            obj.user.handle
        )
    user_link.short_description = 'Recipient'
    
    def type_badge(self, obj):
        colors = {
            'like': '#dc3545',
            'comment': '#007bff',
            'follow': '#28a745',
            'message': '#6f42c1',
            'mention': '#fd7e14'
        }
        color = colors.get(obj.type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'
    
    def content_preview(self, obj):
        preview = obj.content[:70] if obj.content else '(no content)'
        if len(obj.content) > 70:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def sender_link(self, obj):
        if obj.sender:
            url = reverse('admin:users_user_change', args=[obj.sender.pk])
            return format_html(
                '<a href="{}">{} (@{})</a>',
                url,
                obj.sender.display_name,
                obj.sender.handle
            )
        return '—'
    sender_link.short_description = 'From'
    
    def read_status(self, obj):
        if obj.is_read:
            return format_html('✓ <span style="color: #6c757d;">Read</span>')
        return format_html('✗ <span style="color: #dc3545; font-weight: bold;">Unread</span>')
    read_status.short_description = 'Status'
    
    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.user.display_name,
            obj.user.handle,
            obj.user.email
        )
    user_info.short_description = 'Recipient Information'
    
    def sender_info(self, obj):
        if obj.sender:
            return format_html(
                '<strong>{}</strong><br>@{}<br>Email: {}',
                obj.sender.display_name,
                obj.sender.handle,
                obj.sender.email
            )
        return '—'
    sender_info.short_description = 'Sender Information'
    
    def full_content(self, obj):
        return obj.content or '(no content)'
    full_content.short_description = 'Full Content'
