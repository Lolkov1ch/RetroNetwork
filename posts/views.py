from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views import View
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings

from .models import Post
from .forms import PostMediaForm
from posts.mixins import UserIsOwnerMixin
from attachments.models import Media

User = get_user_model()

# custom functions

def handle_media_upload(request, post):
    files = request.FILES.getlist("images")
    
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        messages.error(request, f"Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed.")
        return False
    
    for f in files:
        if f.size > settings.MAX_UPLOAD_SIZE:  
            messages.error(request, f"{f.name} exceeds maximum file size.")
            continue

        media_form = PostMediaForm(files={'file': f})
        if not media_form.is_valid():
            for error in media_form.errors.get('file', []):
                messages.error(request, error)
            continue
        try:
            Media.objects.create(
                user=request.user,
                file=f,
                content_object=post
            )
        except ValidationError as e:
            messages.error(request, str(e))
    
    return True

# classes


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "social_network/post_create.html"
    context_object_name = "post"
    fields = ["title", "description"]
    success_url = reverse_lazy("posts:post_list") 
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        handle_media_upload(self.request, self.object)
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
            post.images = Media.objects.filter(
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id
            )
        return posts


class PostUpdateView(UserIsOwnerMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "social_network/post_edit.html"
    context_object_name = "object"
    fields = ["title", "description"]

    def form_valid(self, form):
        response = super().form_valid(form)

        Media.objects.filter(
            id__in=self.request.POST.getlist("delete_images"),
            user=self.request.user,
            content_object=self.object
        ).delete()

        handle_media_upload(self.request, self.object)
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
        post = get_object_or_404(Post, pk=kwargs["pk"])

        if post.author != request.user:
            messages.error(request, "You don't have permission.")
            return redirect("posts:post_list")

        if not request.FILES.getlist("images"):
            messages.error(request, "No files provided.")
            return redirect("posts:post_list")

        handle_media_upload(request, post)
        messages.success(request, "Files uploaded successfully.")
        return redirect("posts:post_list")

