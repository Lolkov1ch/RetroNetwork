# posts/forms.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image as PilImage

from attachments.models import Media

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}  # mov = quicktime
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/webm", "audio/aac"}

MAX_IMAGE_SIZE = 15 * 1024 * 1024   # 15MB
MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB
MAX_AUDIO_SIZE = 25 * 1024 * 1024   # 25MB


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

        # size guards
        if ct.startswith("image/") and f.size > MAX_IMAGE_SIZE:
            raise ValidationError(f"{f.name}: image is too large.")
        if ct.startswith("video/") and f.size > MAX_VIDEO_SIZE:
            raise ValidationError(f"{f.name}: video is too large.")
        if ct.startswith("audio/") and f.size > MAX_AUDIO_SIZE:
            raise ValidationError(f"{f.name}: audio is too large.")

        # type validation
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

        elif ct.startswith("audio/"):
            if ct not in ALLOWED_AUDIO_TYPES:
                raise ValidationError(f"{f.name}: Unsupported audio type ({ct}).")
            _rewind(f)

        else:
            raise ValidationError(f"{f.name}: File must be an image, video, or audio file.")

        return f