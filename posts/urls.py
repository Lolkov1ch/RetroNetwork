from django.urls import path
from .views import (
    PostListView, 
    PostCreateView, 
    PostUpdateView, 
    PostDeleteView, 
    PostImageView
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("<int:pk>/add-images/", PostImageView.as_view(), name="post_image_upload"),
]
