from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .models import PrivacySettings, ProfileCustomization

User = get_user_model()


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
        fields = ['display_name', 'handle', 'bio', 'email', 'avatar', 'birth_date', 'status']
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
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    pass


class ProfileCustomizationForm(forms.ModelForm):
    class Meta:
        model = ProfileCustomization
        fields = ['cover_photo', 'show_bio', 'show_location', 'show_birth_date', 'show_member_since', 'wall_style']
        widgets = {
            'cover_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'show_bio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_birth_date': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_member_since': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wall_style': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'cover_photo': 'Profile Cover Photo',
            'show_bio': 'Show bio on profile',
            'show_location': 'Show location',
            'show_birth_date': 'Show birth date',
            'show_member_since': 'Show member since',
            'wall_style': 'Wall display style',
        }

