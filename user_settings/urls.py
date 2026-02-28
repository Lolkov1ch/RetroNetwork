from django.urls import path
from .views import (
    PrivacySettingsUpdateView,
    ProfileUpdateView,
    ProfileCustomizeView,
    CustomPasswordChangeView,
    FriendsListView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    RemoveFriendView,
    BlockView,
    UnblockView,
    RecentActivityView,
    FriendRequestsView,
)

app_name = "user_settings"

urlpatterns = [
    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/customize/', ProfileCustomizeView.as_view(), name='profile_customize'),
    path('profile/password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('privacy/', PrivacySettingsUpdateView.as_view(), name='privacy_settings'),
    path('recent-activity/', RecentActivityView.as_view(), name='recent_activity'),
    path('friend-requests/', FriendRequestsView.as_view(), name='friend_requests'),
    path('@<str:handle>/friends/', FriendsListView.as_view(), name='friends_list'),
    path('@<str:handle>/friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('@<str:handle>/accept-friend/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('@<str:handle>/reject-friend/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('@<str:handle>/remove-friend/', RemoveFriendView.as_view(), name='remove_friend'),
    path('@<str:handle>/block/', BlockView.as_view(), name='block'),
    path('@<str:handle>/unblock/', UnblockView.as_view(), name='unblock'),
]

