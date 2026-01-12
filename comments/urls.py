from django.urls import path
from .views import CommentCreateView, CommentDeleteView, CommentEditView

app_name = "comments"

urlpatterns = [
    path("post/<int:pk>/comment/add/", CommentCreateView.as_view(), name="post_add_comment"),
    path("comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"),
    path("comment/<int:pk>/edit/", CommentEditView.as_view(), name="comment_edit"),
]
