from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm    
from .models import NotificationSettings, PrivacySettings, User

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'tag', 'bio', 'email', 'avatar', 'birth_date']


class UserPasswordChangeForm(PasswordChangeForm):
    pass


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = ['likes', 'comments']


class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = PrivacySettings
        fields = ['profile_visibility']