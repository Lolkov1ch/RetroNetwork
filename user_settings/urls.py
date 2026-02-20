from django.urls import path
from .views import (
    NotificationSettingsUpdateView,
    PrivacySettingsUpdateView,
    ProfileUpdateView,
    CustomPasswordChangeView,
    FriendsListView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    BlockView,
    UnblockView,
)

app_name = "user_settings"

urlpatterns = [
    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('notifications/', NotificationSettingsUpdateView.as_view(), name='notification_settings'),
    path('privacy/', PrivacySettingsUpdateView.as_view(), name='privacy_settings'),
    path('@<str:handle>/friends/', FriendsListView.as_view(), name='friends_list'),
    path('@<str:handle>/friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('@<str:handle>/accept-friend/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('@<str:handle>/reject-friend/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('@<str:handle>/block/', BlockView.as_view(), name='block'),
    path('@<str:handle>/unblock/', UnblockView.as_view(), name='unblock'),
]

