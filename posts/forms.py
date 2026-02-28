# posts/forms.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image as PilImage

from attachments.models import Media

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}  # mov = quicktime

MAX_IMAGE_SIZE = 15 * 1024 * 1024   # 15MB
MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB


def _rewind(f):
    try:
        f.seek(0)
    except Exception:
        pass


class PostMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["file"]

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            return f

        ct = (getattr(f, "content_type", "") or "").lower().strip()

        # size guard
        if ct.startswith("image/") and f.size > MAX_IMAGE_SIZE:
            raise ValidationError(f"{f.name}: image is too large.")
        if ct.startswith("video/") and f.size > MAX_VIDEO_SIZE:
            raise ValidationError(f"{f.name}: video is too large.")

        if ct.startswith("image/"):
            if ct not in ALLOWED_IMAGE_TYPES:
                raise ValidationError(f"{f.name}: Unsupported image type ({ct}).")
            try:
                _rewind(f)
                img = PilImage.open(f)
                img.verify()
            except Exception:
                raise ValidationError(f"{f.name}: Invalid image file.")
            finally:
                _rewind(f)

        elif ct.startswith("video/"):
            if ct not in ALLOWED_VIDEO_TYPES:
                raise ValidationError(f"{f.name}: Unsupported video type ({ct}).")
            _rewind(f)

        else:
            raise ValidationError(f"{f.name}: File must be an image or a video.")

        return f