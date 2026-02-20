from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model

from .storage_paths import user_directory_path 
from posts.models import Post

User = get_user_model()

class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    @property
    def is_image(self):
        """Check if media is an image."""
        IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
        return self.file.name.lower().endswith(IMAGE_EXTENSIONS)
    
    @property
    def is_video(self):
        """Check if media is a video."""
        VIDEO_EXTENSIONS = ('.mp4', '.webm', '.avi', '.mov', '.mkv')
        return self.file.name.lower().endswith(VIDEO_EXTENSIONS)
