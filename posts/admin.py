from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_link', 'content_preview', 'media_count', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('author__username', 'author__handle', 'content')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Post Content', {
            'fields': ('author', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
    
    def author_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.author.pk])
        return format_html(
            '<a href="{}">{} (@{})</a>',
            url,
            obj.author.display_name,
            obj.author.handle
        )
    author_link.short_description = 'Author'
    
    def content_preview(self, obj):
        preview = obj.content[:100] if obj.content else '(no content)'
        if len(obj.content) > 100:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def media_count(self, obj):
        media = obj.media_set.count()
        return format_html('📎 {}', media) if media > 0 else '—'
    media_count.short_description = 'Media'
    
    def likes_count(self, obj):
        count = getattr(obj, 'likes_count', 0)
        return format_html('❤️ {}', count)
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        count = getattr(obj, 'comments_count', 0)
        return format_html('💬 {}', count)
    comments_count.short_description = 'Comments'
    
    def is_visible(self, obj):
        return '✓' if obj.id else '✗'
    is_visible.short_description = 'Visible'
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail_url:
            return format_html('<img src="/media/{}" width="200" style="max-height: 200px; border-radius: 4px;"/>', obj.thumbnail_url)
        return 'No thumbnail'
    thumbnail_preview.short_description = 'Thumbnail Preview'
    
    def media_preview(self, obj):
        if hasattr(obj, 'images') and obj.images.exists():
            img = obj.images.first()
            return format_html('<img src="{}" width="200" style="max-height: 200px; border-radius: 4px;"/>', img.file.url)
        elif hasattr(obj, 'videos') and obj.videos.exists():
            return 'Video file present'
        return 'No media'
    media_preview.short_description = 'Media Preview'