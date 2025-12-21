from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from social_network import views

app_name = "social_network"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
