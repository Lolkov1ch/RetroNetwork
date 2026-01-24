from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    tag = models.CharField(max_length=10, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True)
    last_online = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class AccountSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account_settings"
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Account settings for {self.user}"


class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_settings")
    likes = models.BooleanField(default=True)
    comments = models.BooleanField(default=True)


class PrivacySettings(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="privacy_settings")
    profile_visibility = models.CharField(
        max_length=10,
        choices=[("all", "All"),("friends", "Friends"),("none", "Nobody"),],
        default="all"
        )

