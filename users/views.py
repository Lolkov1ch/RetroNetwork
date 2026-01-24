from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import PasswordChangeView
from .models import User, NotificationSettings, PrivacySettings
from .forms import UserProfileForm, UserPasswordChangeForm, NotificationSettingsForm, PrivacySettingsForm

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegisterForm

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
        return render(request, "profile/profile.html", {"user": request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "profile/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "profile/password_change.html"
    success_url = reverse_lazy("users:profile")


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