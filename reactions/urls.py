from django.urls import path
from .views import ToggleLikeView

app_name = "reactions"

urlpatterns = [
    path("like/<str:obj_type>/<int:obj_id>/", ToggleLikeView.as_view(), name="toggle_like"),
]
