from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, MessageReaction, MessageAttachment

User = get_user_model()

from urllib.parse import quote


def avatar_data_uri(handle, size=80):
    if not handle:
        handle = '?'
    AVATAR_COLORS = [
        '#3b5998','#dc3545','#28a745','#007bff','#6f42c1','#fd7e14','#20c997','#17a2b8','#6610f2','#e83e8c'
    ]
    color_index = sum(ord(c) for c in handle.lower()) % len(AVATAR_COLORS)
    color = AVATAR_COLORS[color_index]
    letter = (handle[0].upper() if handle else '?')
    font_size = int(size * 0.5)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"><rect width="100%" height="100%" fill="{color}"/><text x="50%" y="50%" dy=".35em" text-anchor="middle" font-family="Lucida Grande, Tahoma, Verdana, Arial, sans-serif" font-size="{font_size}" fill="#ffffff">{letter}</text></svg>'''
    return 'data:image/svg+xml;utf8,' + quote(svg, safe='')


class UserSimpleSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar']

    def get_avatar(self, obj):
        try:
            if obj.avatar and obj.avatar.name:
                return obj.avatar.url
        except (AttributeError, FileNotFoundError, ValueError):
            pass
        return avatar_data_uri(obj.username, size=80)


class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'attachment_type', 'file', 'thumbnail', 'created_at']
        read_only_fields = ['id', 'thumbnail', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(), write_only=True, required=False
    )
    reactions = MessageReactionSerializer(many=True, read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    is_read = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'conversation',
            'id', 'sender', 'message_type', 'content', 'file', 'image',
            'image_thumbnail', 'video', 'video_thumbnail', 'voice',
            'voice_duration', 'created_at', 'is_edited', 'edited_at',
            'is_read', 'read_count', 'read', 'reactions', 'attachments'
        ]
        read_only_fields = [
            'id', 'sender', 'created_at', 'image_thumbnail',
            'video_thumbnail', 'edited_at', 'attachments'
        ]

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.read_by_users.all()
        return False

    def get_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.read_by_users.all()
        return False

    def get_read_count(self, obj):
        return obj.read_by_users.count()


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSimpleSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    other_user_avatar = serializers.SerializerMethodField()
    other_user_id = serializers.SerializerMethodField()
    other_user_status = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'created_at', 'updated_at', 'is_group',
            'group_name', 'group_avatar', 'last_message', 'last_message_preview',
            'last_message_time', 'unread_count', 'name', 'other_user_avatar', 'other_user_id', 'other_user_status'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_name(self, obj):
        if obj.is_group:
            return obj.group_name or 'Group Chat'

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_users = obj.participants.exclude(id=request.user.id)
            if other_users.exists():
                other_user = other_users.first()
                return other_user.display_name or other_user.username
        
        return 'Chat'

    def get_other_user_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_users = obj.participants.exclude(id=request.user.id)
            if other_users.exists():
                return other_users.first().id
        return None

    def get_other_user_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_users = obj.participants.exclude(id=request.user.id)
            if other_users.exists():
                return other_users.first().status
        return 'offline'

    def get_other_user_avatar(self, obj):
        if obj.is_group and obj.group_avatar:
            return obj.group_avatar.url
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_users = obj.participants.exclude(id=request.user.id)
            if other_users.exists():
                other_user = other_users.first()
                try:
                    if other_user.avatar and other_user.avatar.name:
                        return other_user.avatar.url
                except (AttributeError, FileNotFoundError, ValueError):
                    pass

        return avatar_data_uri(other_user.username if other_user else None, size=80)

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_last_message_preview(self, obj):
        last_message = obj.messages.last()
        if not last_message:
            return 'No messages yet'
        
        if last_message.content:
            preview = last_message.content[:50]
            return preview + '...' if len(last_message.content) > 50 else preview
        elif last_message.message_type == 'image':
            return '📷 Photo'
        elif last_message.message_type == 'video':
            return '🎥 Video'
        elif last_message.message_type == 'voice':
            return '🎤 Voice message'
        elif last_message.message_type == 'file':
            return '📄 File'
        
        return 'Message'

    def get_last_message_time(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return last_message.created_at.isoformat()
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.exclude(sender=request.user).exclude(
                read_by_users=request.user
            ).count()
