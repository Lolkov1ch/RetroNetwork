from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, validate_handle

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your@email.com',
            'class': 'form-control'
        })
    )
    handle = forms.CharField(
        max_length=30,
        validators=[validate_handle],
        help_text="Unique handle (2-30 chars, letters, numbers, _, .)",
        widget=forms.TextInput(attrs={
            'placeholder': 'your_unique_handle',
            'class': 'form-control'
        })
    )
    display_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your public name (optional)',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ("email", "handle", "display_name", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_handle(self):
        handle = self.cleaned_data.get('handle')
        if User.objects.filter(handle=handle).exists():
            raise forms.ValidationError("This handle is already taken.")
        return handle
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.handle = self.cleaned_data['handle']
        user.display_name = self.cleaned_data['display_name']
        
        if commit:
            user.save()
        return user
