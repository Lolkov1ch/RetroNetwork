from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

User = get_user_model()

class Post(models.Model):
    content = models.TextField(default='')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    media_set = GenericRelation('attachments.Media', related_query_name='post')
    
    def __str__(self):
        return self.content[:50]