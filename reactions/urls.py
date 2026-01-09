from django.urls import path
from comments.views import CommentLikeView
from posts.views import PostLikeView
from .views import ToggleLikeView

app_name = "reactions"

urlpatterns = [
    path("like/<str:obj_type>/<int:obj_id>/", ToggleLikeView.as_view(), name="toggle_like"),
    path('post/<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    path('comment/<int:pk>/like/', CommentLikeView.as_view(), name='comment_like'),
]
