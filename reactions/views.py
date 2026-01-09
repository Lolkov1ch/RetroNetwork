from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from posts.models import Post
from comments.models import Comment
from .models import Like

class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, obj_type, obj_id):
        if obj_type == "post":
            obj = get_object_or_404(Post, pk=obj_id)
            like, created = Like.objects.get_or_create(post=obj, user=request.user)
        elif obj_type == "comment":
            obj = get_object_or_404(Comment, pk=obj_id)
            like, created = Like.objects.get_or_create(comment=obj, user=request.user, post=obj.post)
        else:
            messages.error(request, "Invalid like target.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if not created:
            like.delete()
            messages.info(request, f"{obj_type.capitalize()} like removed.")
        else:
            messages.success(request, f"{obj_type.capitalize()} liked!")

        return redirect(request.META.get("HTTP_REFERER", "/"))


class CommentLikeView(View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, comment=comment, post=None)
        if not created:
            like.delete()
            messages.info(request, "Like removed from comment.")
        else:
            messages.success(request, "Comment liked!")
        return redirect("posts:post_detail", pk=comment.post.pk)
    
    
class PostLikeView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post, comment=None)
        if not created:
            like.delete()
            messages.info(request, "Like removed from post.")
        else:
            messages.success(request, "Post liked!")
        return redirect("posts:post_detail", pk=pk)