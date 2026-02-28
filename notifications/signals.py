from django.db.models.signals import post_save
from django.dispatch import receiver
from messaging.models import Message, Conversation
from .models import Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if not created:
        return
    conversation = instance.conversation
    recipients = conversation.participants.exclude(id=instance.sender_id)

    for recipient in recipients:
        Notification.objects.create(
            user=recipient,
            type='message',
            content=instance.content or '[Media message]',
            sender=instance.sender,
            sender_avatar=instance.sender.avatar.url if instance.sender.avatar else '',
            sender_name=instance.sender.display_name or instance.sender.username,
            conversation_id=conversation.id,
            message_id=instance.id,
        )
