from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegisterForm

class LoginView(DjangoLoginView):
    template_name = "login.html"


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
        return redirect("users:login")  


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "profile/profile.html", {"user": request.user})
