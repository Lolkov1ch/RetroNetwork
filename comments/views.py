from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views import View
from django.urls import reverse
from reactions.models import Like
from user_settings.models import Block

from posts.models import Post
from .models import Comment


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "social_network/comment_form.html"
    context_object_name = "comment"
    fields = ["content"]

    def form_valid(self, form):
        post_pk = self.kwargs.get("pk")
        post = get_object_or_404(Post, pk=post_pk)

        is_blocked = Block.objects.filter(blocker=post.author, blocked_user=self.request.user).exists()
        if is_blocked:
            messages.error(self.request, "You cannot comment on this post. You have been blocked by the post author.")
            return redirect(self.request.META.get("HTTP_REFERER", "/"))
        
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs.get("pk")
        context['post'] = get_object_or_404(Post, pk=post_pk)
        return context

    def get_success_url(self):
        messages.success(self.request, "Comment added!")
        return self.request.META.get("HTTP_REFERER", "/")


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "social_network/comment_form.html"
    fields = ["content"]

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            messages.error(request, "You can't edit someone else's comment.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Comment updated!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("posts:post_list")


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if comment.author != request.user:
            messages.error(request, "You can't delete someone else's comment.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        comment.delete()
        messages.success(request, "Comment deleted!")

        return redirect(request.META.get('HTTP_REFERER', '/'))
