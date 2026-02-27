from django.contrib import admin
from .models import Conversation, Message, MessageReaction


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_group', 'created_at', 'updated_at']
    list_filter = ['is_group', 'created_at']
    search_fields = ['group_name', 'participants__display_name']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'message_type', 'conversation', 'created_at', 'is_edited']
    list_filter = ['message_type', 'created_at', 'is_edited']
    search_fields = ['sender__display_name', 'content']
    readonly_fields = ['created_at', 'edited_at', 'read_at']
    filter_horizontal = ['read_by_users']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'reaction_type', 'message', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__display_name']
    readonly_fields = ['created_at']
