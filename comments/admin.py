from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_link', 'post_link', 'content_preview', 'created_at', 'status')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'author__handle', 'post__content')
    readonly_fields = ('created_at', 'author_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'author_info', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def author_link(self, obj):
        """Link to comment author."""
        url = reverse('admin:users_user_change', args=[obj.author.pk])
        return format_html(
            '<a href="{}">{} (@{})</a>',
            url,
            obj.author.display_name,
            obj.author.handle
        )
    author_link.short_description = 'Author'
    
    def post_link(self, obj):
        """Link to parent post."""
        url = reverse('admin:posts_post_change', args=[obj.post.pk])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.pk)
    post_link.short_description = 'Post'
    
    def content_preview(self, obj):
        """Show content preview."""
        preview = obj.content[:80] if obj.content else '(no content)'
        if len(obj.content) > 80:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def status(self, obj):
        """Show comment status."""
        return '✓ Active'
    status.short_description = 'Status'
    
    def author_info(self, obj):
        """Display author info in readonly field."""
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.author.display_name,
            obj.author.handle,
            obj.author.email
        )
    author_info.short_description = 'Author Information'
