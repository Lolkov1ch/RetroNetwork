from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from comments.models import Comment
from .models import Like


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        like, created = Like.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()
            messages.info(request, "Like removed.")
        else:
            messages.success(request, "Comment liked!")
        return redirect("social_network:post_detail", pk=comment.post.pk)
