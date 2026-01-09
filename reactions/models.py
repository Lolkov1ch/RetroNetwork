from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post
from comments.models import Comment

User = get_user_model()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ("user", "post"),
            ("user", "comment"),
        ]

    def is_post_like(self):
        return self.post is not None

    def is_comment_like(self):
        return self.comment is not None
