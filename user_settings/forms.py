from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .models import NotificationSettings, PrivacySettings

User = get_user_model()


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = ['likes', 'comments']
        widgets = {
            'likes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'likes': 'Notify me when someone likes my post',
            'comments': 'Notify me when someone comments on my post',
        }


class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = PrivacySettings
        fields = ['profile_visibility', 'friends_visibility']
        widgets = {
            'profile_visibility': forms.Select(attrs={'class': 'form-select'}),
            'friends_visibility': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'profile_visibility': 'Who can see your profile',
            'friends_visibility': 'Who can see your friends list',
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['display_name', 'handle', 'bio', 'email', 'avatar', 'birth_date']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'placeholder': 'Your public name (can contain spaces)',
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell us about yourself (max 500 chars)',
                'rows': 4,
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    pass

