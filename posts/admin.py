from django.contrib import admin
from .models import Post
from comments.models import Comment

admin.site.register(Post)