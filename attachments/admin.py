from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Media

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'file_type_badge', 'file_preview', 'file_size', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('user__username', 'user__handle', 'file__name')
    readonly_fields = ('user', 'uploaded_at', 'media_preview', 'file_info')
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Media Information', {
            'fields': ('user', 'file_type', 'file_info', 'media_preview')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{} (@{})</a>', url, obj.user.display_name, obj.user.handle)
    user_link.short_description = 'Uploaded by'
    
    def file_type_badge(self, obj):
        colors = {
            'image': '#28a745',
            'video': '#dc3545',
            'audio': '#6f42c1',
            'document': '#007bff',
            'other': '#6c757d'
        }
        color = colors.get(obj.file_type, '#6c757d')
        icons = {
            'image': '📷',
            'video': '🎥',
            'audio': '🎵',
            'document': '📄',
            'other': '📎'
        }
        icon = icons.get(obj.file_type, '📎')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} {}</span>',
            color,
            icon,
            obj.get_file_type_display()
        )
    file_type_badge.short_description = 'Type'
    
    def file_preview(self, obj):
        filename = obj.file.name.split('/')[-1] if obj.file else '(no file)'
        return filename[:40] + '...' if len(filename) > 40 else filename
    file_preview.short_description = 'File'
    
    def file_size(self, obj):
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f'{size:.1f} {unit}'
                size /= 1024
        return '—'
    file_size.short_description = 'Size'
    
    def media_preview(self, obj):
        if obj.file_type == 'image' and obj.file:
            return format_html('<img src="{}" width="300" style="max-height: 300px; border-radius: 4px;"/>', obj.file.url)
        elif obj.file_type == 'video' and obj.file:
            return '🎥 Video file present'
        elif obj.file_type == 'audio' and obj.file:
            return '🎵 Audio file present'
        elif obj.file_type == 'document' and obj.file:
            return '📄 Document file present'
        return '—'
    media_preview.short_description = 'Preview'
    
    def file_info(self, obj):
        if obj.file:
            return format_html(
                '<strong>File:</strong> {}<br><strong>Type:</strong> {}<br><strong>Path:</strong> {}',
                obj.file.name.split('/')[-1],
                obj.get_file_type_display(),
                obj.file.name
            )
        return 'No file'
    file_info.short_description = 'File Information'
