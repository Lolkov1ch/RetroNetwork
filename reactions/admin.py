from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'target_type', 'created_at', 'status')
    list_filter = ('created_at', 'post', 'comment')
    search_fields = ('user__username', 'user__handle', 'post__content', 'comment__content')
    readonly_fields = ('created_at', 'user_info', 'target_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Like Information', {
            'fields': ('user', 'user_info', 'post', 'comment', 'target_info')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Link to user."""
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{} (@{})</a>',
            url,
            obj.user.display_name,
            obj.user.handle
        )
    user_link.short_description = 'User'
    
    def target_type(self, obj):
        """Show what was liked."""
        if obj.post:
            return format_html('❤️ Post #{} by @{}', obj.post.pk, obj.post.author.handle)
        elif obj.comment:
            return format_html('❤️ Comment #{} by @{}', obj.comment.pk, obj.comment.author.handle)
        return '—'
    target_type.short_description = 'Liked'
    
    def status(self, obj):
        """Show like status."""
        return format_html('✓ Active')
    status.short_description = 'Status'
    
    def user_info(self, obj):
        """Display user info in readonly field."""
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.user.display_name,
            obj.user.handle,
            obj.user.email
        )
    user_info.short_description = 'User Information'
    
    def target_info(self, obj):
        """Display target info in readonly field."""
        if obj.post:
            preview = obj.post.content[:100] if obj.post.content else '(no content)'
            if len(obj.post.content) > 100:
                preview += '...'
            return format_html('Post: <em>{}</em>', preview)
        elif obj.comment:
            preview = obj.comment.content[:100] if obj.comment.content else '(no content)'
            if len(obj.comment.content) > 100:
                preview += '...'
            return format_html('Comment: <em>{}</em>', preview)
        return '—'
    target_info.short_description = 'Target Information'
