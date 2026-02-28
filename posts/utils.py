# posts/utils.py
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from attachments.models import Media
from .forms import PostMediaForm
from .models import Post

logger = logging.getLogger(__name__)


def _detect_type(uploaded_file) -> str:
    ct = (getattr(uploaded_file, "content_type", "") or "").lower().strip()
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    return "file"


def handle_media_upload(request, post):
    files = (
        request.FILES.getlist("media_files")
        or request.FILES.getlist("files")
        or request.FILES.getlist("file")
    )

    if not files:
        return

    for f in files:
        form = PostMediaForm(files={"file": f})
        if not form.is_valid():
            errs = form.errors.get("file") or ["Invalid file."]
            for e in errs:
                messages.error(request, str(e))
            continue

        file_type = _detect_type(f)

        try:
            Media.objects.create(
                post=post,
                uploader=request.user,
                file=form.cleaned_data["file"],
                file_type=file_type,  
            )
        except ValidationError as e:
            messages.error(request, f"{f.name}: {e}")
            continue
        except Exception as e:
            logger.warning("Media upload failed for %s", getattr(f, "name", "file"), exc_info=True)
            messages.error(request, f"{getattr(f, 'name', 'file')}: upload failed (invalid/unsupported file).")
            continue


def get_post_media(post_id):
    """Get all media files associated with a post."""
    post_content_type = ContentType.objects.get_for_model(Post)
    return Media.objects.filter(
        content_type=post_content_type,
        object_id=post_id
    ).order_by('uploaded_at')


def is_image(media):
    """Check if a media object is an image."""
    return media.is_image


def is_video(media):
    """Check if a media object is a video."""
    return media.is_video