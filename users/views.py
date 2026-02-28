from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import UpdateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from .models import User, Follow
from .forms import RegisterForm
from user_settings.models import PrivacySettings, Friend, Block, ProfileCustomization
from posts.models import Post
from posts.utils import is_image, is_video, get_post_media
from posts.thumbnail_utils import generate_post_thumbnail

from django.contrib.auth.mixins import LoginRequiredMixin

class LoginView(DjangoLoginView):
    template_name = "registration/login.html"


class RegisterView(View):
    def get(self, request):
        return render(request, "registration/register.html", {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:profile") 
        return render(request, "registration/register.html", {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return render(request, "registration/logged_out.html")


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        posts = Post.objects.filter(author=request.user).order_by('-created_at')

        for post in posts:
            all_media = get_post_media(post.id)
            post.images = [m for m in all_media if is_image(m)]
            post.videos = [m for m in all_media if is_video(m)]
            raw_thumbnail = generate_post_thumbnail(post)
            if raw_thumbnail and not raw_thumbnail.startswith(('/', 'http')):
                from django.conf import settings
                post.thumbnail_url = settings.MEDIA_URL + raw_thumbnail
            else:
                post.thumbnail_url = raw_thumbnail

        try:
            profile_custom = request.user.profile_customization
        except ProfileCustomization.DoesNotExist:
            profile_custom = None

        context = {
            "user": request.user,
            "posts": posts,
            "profile_custom": profile_custom,
        }
        return render(request, "profile/profile.html", context)


class UserSearchView(ListView):
    model = User
    template_name = "users/user_search.html"
    context_object_name = "users"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(handle__icontains=query) | 
                Q(display_name__icontains=query) |
                Q(bio__icontains=query)
            )
        
        return queryset.order_by('handle')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "profile_user"
    slug_field = "handle"
    slug_url_kwarg = "handle"
    
    def get_object(self, queryset=None):
        return get_object_or_404(User, handle=self.kwargs.get('handle'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        current_user = self.request.user
        
        try:
            privacy_settings = profile_user.privacy_settings
        except PrivacySettings.DoesNotExist:
            privacy_settings = PrivacySettings.objects.create(user=profile_user, profile_visibility="all")
        
        try:
            profile_custom = profile_user.profile_customization
        except ProfileCustomization.DoesNotExist:
            profile_custom = None

        can_view = False
        is_own_profile = current_user.is_authenticated and current_user == profile_user
        
        if privacy_settings.profile_visibility == "all":
            can_view = True
        elif privacy_settings.profile_visibility == "none":
            can_view = is_own_profile
        elif privacy_settings.profile_visibility == "friends":
            if is_own_profile:
                can_view = True
            elif current_user.is_authenticated:
                # Check if current user is a friend of the profile owner
                friend_relationship = Friend.objects.filter(
                    Q(requester=current_user, receiver=profile_user, status='accepted') |
                    Q(requester=profile_user, receiver=current_user, status='accepted')
                ).exists()
                can_view = friend_relationship
        
        context['can_view_profile'] = can_view
        context['is_own_profile'] = is_own_profile
        context['privacy_visibility'] = privacy_settings.profile_visibility
        context['profile_custom'] = profile_custom
        
        if can_view:
            posts = Post.objects.filter(author=profile_user).order_by('-created_at')

            for post in posts:
                all_media = get_post_media(post.id)
                post.images = [m for m in all_media if is_image(m)]
                post.videos = [m for m in all_media if is_video(m)]
                post.thumbnail_url = generate_post_thumbnail(post)
            
            context['posts'] = posts
        else:
            context['posts'] = []
        
        if current_user.is_authenticated and not is_own_profile:
            is_blocked = Block.objects.filter(blocker=profile_user, blocked_user=current_user).exists()
            context['is_blocked'] = is_blocked
            
            if not is_blocked and can_view:
                is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
                context['is_following'] = is_following
                
                friend = Friend.objects.filter(
                    Q(requester=current_user, receiver=profile_user) |
                    Q(requester=profile_user, receiver=current_user)
                ).first()
                context['friend_request_status'] = friend.status if friend else None
                context['friend_request'] = friend
                
                is_blocking = Block.objects.filter(blocker=current_user, blocked_user=profile_user).exists()
                context['is_blocking'] = is_blocking
        else:
            context['is_blocked'] = False
        
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        
        if request.user == target_user:
            return redirect('users:user_detail', handle=handle)
        
        Follow.objects.get_or_create(follower=request.user, following=target_user)
        return redirect('users:user_detail', handle=handle)


class UnfollowView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        return redirect('users:user_detail', handle=handle)


class UpdateStatusView(LoginRequiredMixin, View):
    def post(self, request):
        status = request.POST.get('status')
        if status in ['online', 'dnd', 'inactive', 'offline']:
            request.user.status = status
            request.user.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'new_status': status})
        return redirect('users:profile')