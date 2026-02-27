from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from posts.models import Post
from notifications.models import Notification

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if instance.author == post.author:
        return 
    Notification.objects.create(
        user=post.author,
        type='mention',
        content=f'{instance.author.display_name or instance.author.username} commented: {instance.content[:50]}',
        sender=instance.author,
        sender_avatar=instance.author.avatar.url if instance.author.avatar else '',
        sender_name=instance.author.display_name or instance.author.username,
    )
