from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views import View

from .models import Post
from comments.models import Comment
from reactions.models import Like

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "social_network/post_form.html"
    context_object_name = "post"
    fields = ["content"]
    success_url = reverse_lazy("posts:post_list") 
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    template_name = "social_network/post_list.html"
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
        return reverse("posts:post_detail", kwargs={"pk": self.object.pk})  
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "social_network/post_delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("posts:post_list") 
    
