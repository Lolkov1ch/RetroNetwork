from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, AccountSettings, PrivacySettings, NotificationSettings


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        AccountSettings.objects.create(user=instance)
        PrivacySettings.objects.create(user=instance)
        NotificationSettings.objects.create(user=instance)
