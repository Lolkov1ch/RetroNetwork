from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re


def validate_handle(value):
    if not re.match(r'^[a-zA-Z0-9_.]{2,30}$', value):
        raise ValidationError(
            'Handle must be 2-30 characters and contain only letters, numbers, underscores, and dots.'
        )
    if value.startswith('.') or value.endswith('.'):
        raise ValidationError('Handle cannot start or end with a dot.')
    if '..' in value:
        raise ValidationError('Handle cannot contain consecutive dots.')


class User(AbstractUser):
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('dnd', 'Do Not Disturb'),
        ('inactive', 'Inactive'),
        ('offline', 'Offline'),
    ]
    
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=50, blank=True, help_text="Public nickname (can contain spaces)")
    handle = models.CharField(
        max_length=30,
        unique=True,
        validators=[validate_handle],
        help_text="Unique username (2-30 chars, no spaces)"
    )
    bio = models.TextField(blank=True, max_length=500)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    previous_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', help_text="Status before logout")

    def __str__(self):
        return f"@{self.handle}" if self.handle else self.username
    
    def get_display_name(self):
        return self.display_name if self.display_name else self.handle


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]
    
    def __str__(self):
        return f"{self.follower.handle} follows {self.following.handle}"


