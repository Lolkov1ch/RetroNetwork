from django.contrib import admin
from .models import AccountSettings, NotificationSettings, PrivacySettings, ProfileCustomization


@admin.register(AccountSettings)
class AccountSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'password_changed_at')
    list_filter = ('password_changed_at',)
    search_fields = ('user__username', 'user__handle', 'user__email')
    readonly_fields = ('user', 'password_changed_at')


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'likes', 'comments')
    list_filter = ('likes', 'comments')
    search_fields = ('user__username', 'user__handle', 'user__email')
    list_editable = ('likes', 'comments')


@admin.register(PrivacySettings)
class PrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_visibility', 'friends_visibility')
    list_filter = ('profile_visibility', 'friends_visibility')
    search_fields = ('user__username', 'user__handle', 'user__email')
    list_editable = ('profile_visibility', 'friends_visibility')


@admin.register(ProfileCustomization)
class ProfileCustomizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'wall_style')
    list_filter = ('wall_style',)
    search_fields = ('user__username', 'user__handle', 'user__email')
    list_editable = ('wall_style',)

