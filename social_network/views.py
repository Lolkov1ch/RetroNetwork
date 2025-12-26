from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.urls import reverse_lazy, reverse
from social_network.models import Post, Comment, Like
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from django.core.exceptions import PermissionDenied


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "social_network/post_form.html"
    context_object_name = "post"
    fields = ["content"]
    success_url = reverse_lazy("social_network:post_base")
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    template_name = "social_network/post_base.html"
    context_object_name = "posts"
    paginate_by = 10
    

class PostDetailView(DetailView):
    model = Post
    template_name = "social_network/post_detail.html"


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "social_network/post_form.html"
    context_object_name = "post"
    fields = ["content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("social_network:post_detail", kwargs={"pk": self.object.pk})
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "social_network/post_delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("social_network:post_base")
    

class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )

        if not created:
            like.delete()
            messages.info(request, "Like removed.")
        else:
            messages.success(request, "Post liked!")

        return redirect("social_network:post_detail", pk=post.pk)


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


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        like, created = Like.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()
            messages.info(request, "Like removed.")
        else:
            messages.success(request, "Comment liked!")
        return redirect("social_network:post_detail", pk=comment.post.pk)