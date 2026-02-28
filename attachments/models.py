from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model

from .storage_paths import user_directory_path
from .validators import validate_upload_file, get_file_type

User = get_user_model()

class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[validate_upload_file],
        help_text='Maximum file size depends on file type'
    )
    file_type = models.CharField(
        max_length=20,
        default='unknown',
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('document', 'Document'),
            ('unknown', 'Unknown'),
        ],
        db_index=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['file_type', '-uploaded_at']),
        ]
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_type = get_file_type(self.file.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} - {self.file.name}'
    
    @property
    def file_size_mb(self):
        return round(self.file.size / (1024 * 1024), 2) if self.file else 0
    
    @property
    def is_image(self):
        return self.file_type == 'image'
    
    @property
    def is_video(self):
        return self.file_type == 'video'
    
    @property
    def is_audio(self):
        return self.file_type == 'audio'
    
    @property
    def is_document(self):
        return self.file_type == 'document'
