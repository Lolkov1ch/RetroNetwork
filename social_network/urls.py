from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from social_network import views
from .views import (PostListView, 
                    PostDetailView, 
                    PostCreateView, 
                    PostUpdateView, 
                    PostDeleteView, 
                    PostLikeView, 
                    CommentCreateView,
                    CommentDeleteView,
                    CommentEditView,
                    ToggleLikeView)


app_name = "social_network"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_base"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/like/", views.PostLikeView.as_view(), name="post_like"),
    path("post/<int:pk>/comment/add/", views.CommentCreateView.as_view(), name="post_add_comment"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"), 
    path("comment/<int:pk>/edit/", views.CommentEditView.as_view(), name="comment_edit"),
    path("like/<str:obj_type>/<int:obj_id>/", views.ToggleLikeView.as_view(), name="toggle_like"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
