from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic import ListView, DetailView
from django.views import View
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import NotificationSettings, PrivacySettings, Friend, Block, ProfileCustomization
from .forms import (
    NotificationSettingsForm, 
    PrivacySettingsForm, 
    UserProfileForm, 
    UserPasswordChangeForm,
    ProfileCustomizationForm
)

User = get_user_model()


class NotificationSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = "profile/notification_settings.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return NotificationSettings.objects.get_or_create(user=self.request.user)[0]


class PrivacySettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = PrivacySettings
    form_class = PrivacySettingsForm
    template_name = "profile/privacy_settings.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return PrivacySettings.objects.get_or_create(user=self.request.user)[0]


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "profile/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
        
        return response


class ProfileCustomizeView(LoginRequiredMixin, UpdateView):
    model = ProfileCustomization
    form_class = ProfileCustomizationForm
    template_name = "profile/profile_customize.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        obj, created = ProfileCustomization.objects.get_or_create(user=self.request.user)
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.request.user
        return context


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "profile/password_change.html"
    success_url = reverse_lazy("users:profile")


class FriendsListView(DetailView):
    model = User
    template_name = "users/friends_list.html"
    context_object_name = "profile_user"
    slug_field = "handle"
    slug_url_kwarg = "handle"
    
    def get_object(self, queryset=None):
        return get_object_or_404(User, handle=self.kwargs.get('handle'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        current_user = self.request.user
        is_own_profile = current_user.is_authenticated and current_user == profile_user
        
        try:
            privacy_settings = profile_user.privacy_settings
        except PrivacySettings.DoesNotExist:
            privacy_settings = PrivacySettings.objects.create(user=profile_user)
        
        is_blocked = False
        if current_user.is_authenticated and not is_own_profile:
            is_blocked = Block.objects.filter(blocker=profile_user, blocked_user=current_user).exists()

        can_view_friends = False
        if is_own_profile:
            can_view_friends = True
        elif is_blocked:
            can_view_friends = False
        elif privacy_settings.friends_visibility == "all":
            can_view_friends = True
        elif privacy_settings.friends_visibility == "friends":
            can_view_friends = False
            if current_user.is_authenticated:
                can_view_friends = Friend.objects.filter(
                    Q(requester=current_user, receiver=profile_user, status="accepted") |
                    Q(requester=profile_user, receiver=current_user, status="accepted")
                ).exists()
        elif privacy_settings.friends_visibility == "none":
            can_view_friends = is_own_profile
        
        context['is_own_profile'] = is_own_profile
        context['is_blocked'] = is_blocked
        context['can_view_friends'] = can_view_friends
        
        if can_view_friends:
            friends = User.objects.filter(
                Q(friend_requests_received__requester=profile_user, friend_requests_received__status="accepted") |
                Q(friend_requests_sent__receiver=profile_user, friend_requests_sent__status="accepted")
            ).distinct()
            context['friends'] = friends
        else:
            context['friends'] = []
        
        return context


class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        
        if request.user == target_user:
            return redirect('users:user_detail', handle=handle)

        existing = Friend.objects.filter(
            Q(requester=request.user, receiver=target_user) |
            Q(requester=target_user, receiver=request.user)
        ).first()
        
        if not existing:
            Friend.objects.create(requester=request.user, receiver=target_user, status="pending")
        
        return redirect('users:user_detail', handle=handle)


class AcceptFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, handle):
        requester = get_object_or_404(User, handle=handle)
        
        friend = Friend.objects.filter(requester=requester, receiver=request.user, status="pending").first()
        if friend:
            friend.status = "accepted"
            friend.save()
        
        return redirect('users:user_detail', handle=handle)


class RejectFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, handle):
        requester = get_object_or_404(User, handle=handle)
        
        friend = Friend.objects.filter(requester=requester, receiver=request.user, status="pending").first()
        if friend:
            friend.delete()
        
        return redirect('users:user_detail', handle=handle)


class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        
        Friend.objects.filter(
            Q(requester=request.user, receiver=target_user, status="accepted") |
            Q(requester=target_user, receiver=request.user, status="accepted")
        ).delete()
        
        return redirect('users:user_detail', handle=handle)


class BlockView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        
        if request.user == target_user:
            return redirect('users:user_detail', handle=handle)
        
        Block.objects.get_or_create(blocker=request.user, blocked_user=target_user)

        from users.models import Follow
        Follow.objects.filter(
            Q(follower=request.user, following=target_user) |
            Q(follower=target_user, following=request.user)
        ).delete()

        Friend.objects.filter(
            Q(requester=request.user, receiver=target_user) |
            Q(requester=target_user, receiver=request.user)
        ).delete()
        
        return redirect('users:user_detail', handle=handle)


class UnblockView(LoginRequiredMixin, View):
    def post(self, request, handle):
        target_user = get_object_or_404(User, handle=handle)
        Block.objects.filter(blocker=request.user, blocked_user=target_user).delete()
        return redirect('users:user_detail', handle=handle)


class RecentActivityView(LoginRequiredMixin, ListView):
    model = User
    template_name = "user_settings/recent_activity.html"
    context_object_name = "activities"
    paginate_by = 20

    def get_queryset(self):
        from posts.models import Post
        from comments.models import Comment
        
        following_ids = self.request.user.following.values_list('following_id', flat=True)
        
        if not following_ids.exists():
            return []
        
        posts = Post.objects.filter(author_id__in=following_ids).select_related('author').order_by('-created_at')[:50]
        
        return posts
    
    def get_context_data(self, **kwargs):
        from notifications.models import Notification
        context = super().get_context_data(**kwargs)
        context['posts'] = context.pop('activities')
        context['notifications'] = Notification.objects.filter(user=self.request.user).select_related('sender').order_by('-created_at')[:50]
        context['unread_count'] = Notification.objects.filter(user=self.request.user, is_read=False).count()
        return context


class FriendRequestsView(LoginRequiredMixin, ListView):
    model = Friend
    template_name = "user_settings/friend_requests.html"
    context_object_name = "friend_requests"
    paginate_by = 20

    def get_queryset(self):
        return Friend.objects.filter(receiver=self.request.user, status='pending').select_related('requester').order_by('-created_at')
