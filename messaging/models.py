from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image
from io import BytesIO

User = get_user_model()


def get_message_upload_path(instance, filename):
    return f'messenger/{instance.sender_id}/{filename}'


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_group = models.BooleanField(default=False, db_index=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    group_avatar = models.ImageField(upload_to='conversation_avatars/', blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['is_group', '-updated_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        if self.is_group:
            return self.group_name or "Group Conversation"
        participants = list(self.participants.all())
        return f"Conversation: {', '.join([p.display_name for p in participants])}"

    def get_other_user(self, user):
        if not self.is_group:
            return self.participants.exclude(pk=user.pk).first()
        return None

    def mark_as_read(self, user):
        self.messages.filter(read_by_users__isnull=True).exclude(sender=user).update(
            read_at=timezone.now()
        )
        for message in self.messages.exclude(sender=user):
            if user not in message.read_by_users.all():
                message.read_by_users.add(user)


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('video', 'Video'),
        ('voice', 'Voice'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text',
        db_index=True
    )
    content = models.TextField(blank=True)
    file = models.FileField(upload_to=get_message_upload_path, blank=True, null=True)
    image = models.ImageField(upload_to=get_message_upload_path, blank=True, null=True)
    image_thumbnail = models.ImageField(
        upload_to=get_message_upload_path,
        blank=True,
        null=True
    )
    video = models.FileField(upload_to=get_message_upload_path, blank=True, null=True)
    video_thumbnail = models.ImageField(
        upload_to=get_message_upload_path,
        blank=True,
        null=True
    )
    voice = models.FileField(upload_to=get_message_upload_path, blank=True, null=True)
    voice_duration = models.FloatField(default=0)  # in seconds

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True, db_index=True)
    read_by_users = models.ManyToManyField(User, related_name='read_messages', blank=True)
    
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['conversation', 'message_type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.display_name} - {self.created_at}"

    def mark_as_read(self, user):
        if user not in self.read_by_users.all() and user != self.sender:
            self.read_by_users.add(user)
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    def mark_as_delivered(self):
        pass

    def generate_image_thumbnail(self):
        if self.image:
            try:
                img = Image.open(self.image)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG', quality=80)
                thumb_io.seek(0)
                
                thumb_name = f"thumb_{self.image.name.split('/')[-1]}"
                self.image_thumbnail.save(thumb_name, thumb_io, save=False)
            except Exception as e:
                print(f"Error generating image thumbnail: {e}")

    def generate_video_thumbnail(self):
        if self.video and not self.video_thumbnail:
            img = Image.new('RGB', (320, 180), color=(52, 91, 165))
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=80)
            thumb_io.seek(0)
            
            thumb_name = f"thumb_{self.video.name.split('/')[-1]}.jpg"
            self.video_thumbnail.save(thumb_name, thumb_io, save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            if self.message_type == 'image':
                self.generate_image_thumbnail()
                self.save(update_fields=['image_thumbnail'])
            elif self.message_type == 'video':
                self.generate_video_thumbnail()
                self.save(update_fields=['video_thumbnail'])


class MessageReaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions',
        db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f"{self.user.display_name} reacted {self.reaction_type} to {self.message}"
