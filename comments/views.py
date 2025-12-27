from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied

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
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs.get("pk")
        context['post'] = get_object_or_404(Post, pk=post_pk)
        return context

    def get_success_url(self):
        post_pk = self.kwargs.get("pk")
        return reverse("social_network:post_detail", kwargs={"pk": post_pk})


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "social_network/comment_form.html"
    context_object_name = "comment"
    fields = ["content"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object.post
        return context

    def get_success_url(self):
        messages.success(self.request, "Comment updated!")
        return reverse("social_network:post_detail", kwargs={"pk": self.object.post.pk})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            messages.error(request, "You can't edit someone else's comment.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "social_network/comment_delete.html"
    context_object_name = "comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object.post
        return context

    def get_success_url(self):
        messages.success(self.request, "Comment deleted!")
        return reverse("social_network:post_detail", kwargs={"pk": self.object.post.pk})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            messages.error(request, "You can't delete someone else's comment.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
