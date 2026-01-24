from django.urls import path
from .views import (LoginView,
                    RegisterView, 
                    LogoutView, 
                    ProfileView, 
                    ProfileUpdateView, 
                    CustomPasswordChangeView, 
                    NotificationSettingsUpdateView, 
                    PrivacySettingsUpdateView)

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('profile/notifications/', NotificationSettingsUpdateView.as_view(), name='notification_settings'),
    path('profile/privacy/', PrivacySettingsUpdateView.as_view(), name='privacy_settings'),
]
