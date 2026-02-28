from django.urls import path
from .views import (LoginView,
                    RegisterView, 
                    LogoutView, 
                    ProfileView, 
                    UserSearchView,
                    UserDetailView,
                    FollowView,
                    UnfollowView,
                    UpdateStatusView)

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('status/update/', UpdateStatusView.as_view(), name='update_status'),
    path('@<str:handle>/follow/', FollowView.as_view(), name='follow'),
    path('@<str:handle>/unfollow/', UnfollowView.as_view(), name='unfollow'),
    path('@<str:handle>/', UserDetailView.as_view(), name='user_detail'),
]
