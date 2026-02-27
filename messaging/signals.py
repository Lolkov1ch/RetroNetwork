from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Message
from .serializers import MessageSerializer
import json


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    if not created:
        return
    
    try:
        channel_layer = get_channel_layer()
        conversation_id = instance.conversation.id
        conversation_group_name = f'chat_{conversation_id}'

        message_data = MessageSerializer(instance).data

        async_to_sync(channel_layer.group_send)(
            conversation_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
        
        print(f"[Messaging Signal] Broadcasted message {instance.id} to group {conversation_group_name}")
    except Exception as e:
        print(f"[Messaging Signal] Error broadcasting message: {e}")
