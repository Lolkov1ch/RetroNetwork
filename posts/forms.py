from django import forms
from attachments.models import Image


class PostImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file'] 