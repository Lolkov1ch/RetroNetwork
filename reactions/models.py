from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post      
from comments.models import Comment 

User = get_user_model()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} likes Post #{self.post.id}"

    class Meta:
        unique_together = ("post", "user", "comment")