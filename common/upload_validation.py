from django.core.exceptions import ValidationError
from PIL import Image as PilImage

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/ogg", "audio/webm", "audio/mpeg", "audio/wav", "audio/aac", "audio/mp4"}

def rewind(f):
    try:
        f.seek(0)
    except Exception:
        pass

def validate_upload(f, *, kind: str = "any"):
    """
    kind: 'any' | 'image' | 'video' | 'audio'
    """
    if not f:
        return

    ct = (getattr(f, "content_type", "") or "").lower()
    rewind(f)

    if kind in ("any", "image") and ct.startswith("image/"):
        if ct not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(f"{f.name}: Unsupported image type ({ct}).")
        try:
            img = PilImage.open(f)
            img.verify()
        except Exception:
            raise ValidationError(f"{f.name}: Invalid image file.")
        finally:
            rewind(f)
        return

    if kind in ("any", "video") and ct.startswith("video/"):
        if ct not in ALLOWED_VIDEO_TYPES:
            raise ValidationError(f"{f.name}: Unsupported video type ({ct}).")
        rewind(f)
        return

    if kind in ("any", "audio") and ct.startswith("audio/"):
        if ct not in ALLOWED_AUDIO_TYPES:
            raise ValidationError(f"{f.name}: Unsupported audio type ({ct}).")
        rewind(f)
        return

    raise ValidationError(f"{f.name}: File type not allowed ({ct}).")