from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views import View
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Post
from .forms import PostMediaForm
from posts.mixins import UserIsOwnerMixin
from attachments.models import Media
from posts.utils import is_image, is_video, get_post_media, handle_media_upload
from posts.thumbnail_utils import generate_post_thumbnail

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "social_network/post_create.html"
    context_object_name = "post"
    fields = ["content"]
    success_url = reverse_lazy("posts:post_list")
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        handle_media_upload(self.request, self.object)
        return response


class PostListView(ListView):
    """
    Display a paginated list of posts with search functionality.
    Posts are ordered by engagement metrics (likes, comments, views).
    """
    model = Post
    template_name = "social_network/post_list.html"
    context_object_name = "posts"
    paginate_by = 10
    
    def get_queryset(self):
        """
        Get optimized queryset with prefetch_related to avoid N+1 queries.
        """
        queryset = super().get_queryset().select_related('author')
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(content__icontains=query)
            )

        posts = queryset.annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).order_by('-like_count', '-comment_count', '-views', '-id')
        
        for post in posts:
            all_media = get_post_media(post.id)
            post.images = [m for m in all_media if is_image(m)]
            post.videos = [m for m in all_media if is_video(m)]
            
            post.thumbnail_url = generate_post_thumbnail(post)
            
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = "social_network/post_detail.html"
    context_object_name = "post"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['media_files'] = get_post_media(post.id)
        return context
    
    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.views += 1
        post.save(update_fields=['views'])
        return post

class PostUpdateView(UserIsOwnerMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "social_network/post_edit.html"
    context_object_name = "object"
    fields = ["content"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_files'] = get_post_media(self.object.id)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        Media.objects.filter(
            id__in=self.request.POST.getlist("delete_images"),
            user=self.request.user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.object.id
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


class PostSearchView(ListView):
    model = Post
    template_name = "social_network/post_search.html"
    context_object_name = "posts"
    paginate_by = 10
    
    def get_queryset(self):
        """
        Get search results with optimized queries.
        """
        queryset = super().get_queryset().select_related('author')
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(content__icontains=query) | Q(author__username__icontains=query)
            )
        
        posts = queryset.annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).order_by('-like_count', '-comment_count', '-views', '-id')
        
        for post in posts:
            all_media = get_post_media(post.id)
            post.images = [m for m in all_media if is_image(m)]
            post.videos = [m for m in all_media if is_video(m)]

            post.thumbnail_url = generate_post_thumbnail(post)
            
        return posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PostAPIView(View):
    
    def get(self, request):
        page = int(request.GET.get('page', 1))
        query = request.GET.get('q', '')
        per_page = 10
        
        posts_qs = Post.objects.all()
        
        if query:
            posts_qs = posts_qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        posts_qs = posts_qs.order_by('-id')

        start = (page - 1) * per_page
        end = start + per_page
        
        posts = posts_qs[start:end]
        total_count = posts_qs.count()

        posts_list = []
        for post in posts:
            all_media = get_post_media(post.id)
            post.images = [m for m in all_media if is_image(m)]
            post.videos = [m for m in all_media if is_video(m)]
            post.thumbnail_url = generate_post_thumbnail(post)
            
            posts_list.append(post)

        html = render_to_string('social_network/post_item.html', {
            'posts': posts_list,
            'user': request.user
        })

        has_more = end < total_count
        
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'page': page,
            'total_count': total_count
        })