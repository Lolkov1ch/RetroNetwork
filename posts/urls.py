from django.urls import path
from .views import (
    PostListView, 
    PostCreateView, 
    PostUpdateView, 
    PostDeleteView, 
    PostImageView,
    PostSearchView,
    PostDetailView,
    PostAPIView
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("api/posts/", PostAPIView.as_view(), name="posts_api"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("search/", PostSearchView.as_view(), name="post_search"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("<int:pk>/add-images/", PostImageView.as_view(), name="post_image_upload"),
]
