from urllib import request
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import get_image_dimensions
from django.contrib.auth import get_user_model
from django.views import View
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from .models import Post
from posts.mixins import UserIsOwnerMixin
from attachments.models import Image
from comments.models import Comment
from reactions.models import Like

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "social_network/post_form.html"
    context_object_name = "post"
    fields = ["title", "description"]
    success_url = reverse_lazy("posts:post_list") 
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        images = self.request.FILES.getlist("images")  
        for f in images:
            Image.objects.create(
                user=self.request.user,
                file=f,
                content_object=self.object  
            )

        return response


class PostListView(ListView):
    model = Post
    template_name = "social_network/post_list.html"
    context_object_name = "posts"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        posts = queryset.order_by('-id')
        for post in posts:
            post.images = Image.objects.filter(
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id
            )
        return posts


class PostUpdateView(UserIsOwnerMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "social_network/post_form.html"
    context_object_name = "post"
    fields = ["title", "description"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        images = self.request.FILES.getlist("images")
        for f in images:
            Image.objects.create(
                user=self.request.user,
                file=f,
                content_object=self.object
            )

        return response 

    def get_success_url(self):
        return reverse("posts:post_list")  


class PostDeleteView(UserIsOwnerMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "social_network/post_delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("posts:post_list") 


class PostImageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get("pk"))

        files = request.FILES.getlist("images")
        if not files:
            messages.error(request, "No image files provided.")
            return redirect("posts:post_list")

        for f in files:
            Image.objects.create(
                user=request.user, 
                file=f,
                content_object=post
            )

        post = get_object_or_404(Post, pk=kwargs.get("pk"))
        if post.author != request.user:
            messages.error(request, "You don't have permission to add images to this post.")
            return redirect("posts:post_list")

        messages.success(request, "Images uploaded successfully.")
        return redirect("posts:post_list")