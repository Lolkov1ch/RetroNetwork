from django.contrib import admin
from attachments.models import Image
from .models import Post
from comments.models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')

admin.site.register(Post)