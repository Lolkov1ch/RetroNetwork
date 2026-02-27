from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from notifications.models import Notification

@receiver(post_save, sender=Post)
def create_post_notification(sender, instance, created, **kwargs):
    if not created:
        return
    pass
