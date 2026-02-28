from django import forms
from django.core.exceptions import ValidationError
from PIL import Image as PilImage

from attachments.models import Media

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}

class PostMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["file"]

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            return f

        content_type = getattr(f, "content_type", "") or ""

        if content_type.startswith("image/"):
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise ValidationError(f"{f.name}: Unsupported image type ({content_type}).")

            try:
                f.seek(0)
                img = PilImage.open(f)
                img.verify()  
            except Exception:
                raise ValidationError(f"{f.name}: Invalid image file.")
            f.seek(0)

        elif content_type.startswith("video/"):
            if content_type not in ALLOWED_VIDEO_TYPES:
                raise ValidationError(f"{f.name}: Unsupported video type ({content_type}).")

        else:
            raise ValidationError(f"{f.name}: File must be an image or video.")

        return f