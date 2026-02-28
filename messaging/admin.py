from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Conversation, Message, MessageReaction, MessageAttachment


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_badge', 'participants_count', 'message_count', 'last_activity', 'created_at')
    list_filter = ('is_group', 'created_at', 'updated_at')
    search_fields = ('group_name', 'participants__display_name', 'participants__handle')
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at', 'participants_list')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Conversation Information', {
            'fields': ('is_group', 'group_name', 'group_avatar', 'participants', 'participants_list')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            message_count=Count('messages', distinct=True),
            participant_count=Count('participants', distinct=True)
        )
    
    def name(self, obj):
        if obj.is_group:
            return format_html('👥 {}', obj.group_name or 'Unnamed Group')
        else:
            other = obj.participants.exclude(id=1).first() if obj.participants.exists() else None
            name = f"{other.display_name} (@{other.handle})" if other else "Direct Message"
            return format_html('💬 {}', name)
    name.short_description = 'Conversation'
    
    def type_badge(self, obj):
        if obj.is_group:
            return '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">Group</span>'
        return '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Direct</span>'
    type_badge.short_description = 'Type'
    
    def participants_count(self, obj):
        count = getattr(obj, 'participant_count', 0)
        return format_html('👥 {}', count)
    participants_count.short_description = 'Participants'
    
    def message_count(self, obj):
        count = getattr(obj, 'message_count', 0)
        return format_html('💬 {}', count)
    message_count.short_description = 'Messages'
    
    def last_activity(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    last_activity.short_description = 'Last Activity'
    
    def participants_list(self, obj):
        participants = obj.participants.all()
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for participant in participants:
            html += f'<li>{participant.display_name} (@{participant.handle})</li>'
        html += '</ul>'
        return format_html(html)
    participants_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_link', 'conversation_link', 'type_badge', 'content_preview', 'read_status', 'created_at')
    list_filter = ('message_type', 'created_at', 'is_edited')
    search_fields = ('sender__username', 'sender__handle', 'content', 'conversation__group_name')
    readonly_fields = ('created_at', 'edited_at', 'read_at', 'message_preview', 'sender_info')
    date_hierarchy = 'created_at'
    filter_horizontal = ('read_by_users',)
    
    fieldsets = (
        ('Message Information', {
            'fields': ('sender', 'sender_info', 'conversation', 'message_type', 'content', 'message_preview')
        }),
        ('Files & Reactions', {
            'fields': ('image', 'video', 'file'),
            'classes': ('collapse',)
        }),
        ('Read Status', {
            'fields': ('read_by_users', 'read_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'edited_at', 'is_edited'),
            'classes': ('collapse',)
        }),
    )
    
    def sender_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.sender.pk])
        return format_html(
            '<a href="{}">{} (@{})</a>',
            url,
            obj.sender.display_name,
            obj.sender.handle
        )
    sender_link.short_description = 'Sender'
    
    def conversation_link(self, obj):
        url = reverse('admin:messaging_conversation_change', args=[obj.conversation.pk])
        name = obj.conversation.group_name or f"Direct Message #{obj.conversation.pk}"
        return format_html('<a href="{}">{}</a>', url, name)
    conversation_link.short_description = 'Conversation'
    
    def type_badge(self, obj):
        colors = {
            'text': '#007bff',
            'image': '#28a745',
            'video': '#dc3545',
            'file': '#6f42c1'
        }
        color = colors.get(obj.message_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_message_type_display()
        )
    type_badge.short_description = 'Type'
    
    def content_preview(self, obj):
        if obj.message_type == 'text':
            preview = obj.content[:80] if obj.content else '(no content)'
            if len(obj.content) > 80:
                preview += '...'
            return preview
        elif obj.message_type == 'image':
            return '📷 Image'
        elif obj.message_type == 'video':
            return '🎥 Video'
        elif obj.message_type == 'file':
            return '📎 File'
        return '—'
    content_preview.short_description = 'Content'
    
    def read_status(self, obj):
        read_count = obj.read_by_users.count()
        if read_count > 0:
            return format_html('✓ Read by {}', read_count)
        return '✗ Unread'
    read_status.short_description = 'Status'
    
    def message_preview(self, obj):
        if obj.message_type == 'image' and obj.image:
            return format_html('<img src="{}" width="200" style="max-height: 200px; border-radius: 4px;"/>', obj.image.url)
        elif obj.message_type == 'text':
            return obj.content or '(no content)'
        elif obj.message_type == 'video' and obj.video:
            return '🎥 Video file present'
        elif obj.message_type == 'file' and obj.file:
            return format_html('📎 File: {}', obj.file.name.split('/')[-1])
        return '—'
    message_preview.short_description = 'Preview'
    
    def sender_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.sender.display_name,
            obj.sender.handle,
            obj.sender.email
        )
    sender_info.short_description = 'Sender Information'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'message_link', 'reaction_badge', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'user__handle', 'message__content')
    readonly_fields = ('created_at', 'user_info', 'message_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Reaction Information', {
            'fields': ('user', 'user_info', 'message', 'message_info', 'reaction_type')
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
    user_link.short_description = 'User'
    
    def reaction_badge(self, obj):
        emoji_map = {
            'like': '👍',
            'love': '❤️',
            'haha': '😂',
            'wow': '😮',
            'sad': '😢',
            'angry': '😠',
        }
        emoji = emoji_map.get(obj.reaction_type, '👍')
        return format_html('{} {}', emoji, obj.get_reaction_type_display())
    reaction_badge.short_description = 'Reaction'
    
    def message_link(self, obj):
        url = reverse('admin:messaging_message_change', args=[obj.message.pk])
        return format_html('<a href="{}">Message #{}</a>', url, obj.message.pk)
    message_link.short_description = 'Message'
    
    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>@{}<br>Email: {}',
            obj.user.display_name,
            obj.user.handle,
            obj.user.email
        )
    user_info.short_description = 'User Information'
    
    def message_info(self, obj):
        preview = obj.message.content[:100] if obj.message.message_type == 'text' else f'({obj.message.get_message_type_display()})'
        return format_html('<em>{}</em>', preview)
    message_info.short_description = 'Message'


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_link', 'attachment_type_badge', 'file_preview', 'created_at')
    list_filter = ('attachment_type', 'created_at')
    search_fields = ('message__id', 'file')
    readonly_fields = ('created_at', 'message_info', 'preview')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Attachment Information', {
            'fields': ('message', 'message_info', 'attachment_type', 'file', 'preview')
        }),
        ('Thumbnail', {
            'fields': ('thumbnail',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def message_link(self, obj):
        url = reverse('admin:messaging_message_change', args=[obj.message.pk])
        return format_html('<a href="{}">Message #{}</a>', url, obj.message.pk)
    message_link.short_description = 'Message'
    
    def attachment_type_badge(self, obj):
        colors = {
            'image': '#28a745',
            'video': '#dc3545',
        }
        color = colors.get(obj.attachment_type, '#6c757d')
        emoji = '📷' if obj.attachment_type == 'image' else '🎥'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} {}</span>',
            color,
            emoji,
            obj.get_attachment_type_display()
        )
    attachment_type_badge.short_description = 'Type'
    
    def file_preview(self, obj):
        filename = obj.file.name.split('/')[-1]
        return format_html('<code>{}</code>', filename)
    file_preview.short_description = 'File'
    
    def preview(self, obj):
        if obj.attachment_type == 'image' and obj.file:
            return format_html('<img src="{}" width="300" style="max-height: 300px; border-radius: 4px;"/>', obj.file.url)
        elif obj.attachment_type == 'video' and obj.thumbnail:
            return format_html('<img src="{}" width="300" style="max-height: 300px; border-radius: 4px;"/>', obj.thumbnail.url)
        return '—'
    preview.short_description = 'Preview'
    
    def message_info(self, obj):
        message_type = obj.message.get_message_type_display()
        sender = obj.message.sender.display_name
        return format_html(
            'Type: <strong>{}</strong><br>Sender: <strong>{}</strong>',
            message_type,
            sender
        )
    message_info.short_description = 'Message Information'

