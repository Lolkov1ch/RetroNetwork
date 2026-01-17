from django import forms
from PIL import Image as PilImage
from attachments.models import Media
from django.core.exceptions import ValidationError
from django.contrib import messages

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/mov']

class PostMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        content_type = file.content_type

        if content_type.startswith('image/'):
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError(f"{file.name}: Unsupported image type.")
            try:
                img = PilImage.open(file)
                img.verify()
            except Exception:
                raise ValidationError(f"{file.name}: Invalid image file.")

        elif content_type.startswith('video/'):
            if content_type not in ALLOWED_VIDEO_TYPES:
                raise ValidationError(f"{file.name}: Unsupported video type.")

        else:
            raise ValidationError(f"{file.name}: File must be an image or video.")

        return file
