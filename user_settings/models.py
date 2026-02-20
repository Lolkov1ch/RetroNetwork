from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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

    def __str__(self):
        return f"Notification settings for {self.user}"


class PrivacySettings(models.Model):
    VISIBILITY_CHOICES = [("all", "Everyone"), ("friends", "Friends only"), ("none", "Only me")]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="privacy_settings")
    profile_visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="all"
    )
    friends_visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="all",
        help_text="Who can see your friends list"
    )

    def __str__(self):
        return f"Privacy settings for {self.user}"


class Friend(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_received")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('requester', 'receiver')
        indexes = [
            models.Index(fields=['requester', 'receiver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.requester.handle} - {self.receiver.handle} ({self.status})"


class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('blocker', 'blocked_user')
        indexes = [
            models.Index(fields=['blocker', 'blocked_user']),
        ]
    
    def __str__(self):
        return f"{self.blocker.handle} blocked {self.blocked_user.handle}"

