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
    if ct.startswith("audio/"):
        return "audio"
    return "document"


def handle_media_upload(request, post):
    files = (
        request.FILES.getlist("media_files")
        or request.FILES.getlist("images")
        or request.FILES.getlist("videos")
        or request.FILES.getlist("files")
        or request.FILES.getlist("file")
    )

    logger.info(f"handle_media_upload called with {len(files)} files for post {post.id}")
    if not files:
        logger.warning("No files found in request.FILES")
        return False

    uploaded_any = False
    post_content_type = ContentType.objects.get_for_model(Post)

    for f in files:
        form = PostMediaForm(files={"file": f})
        if not form.is_valid():
            errs = form.errors.get("file") or ["Invalid file."]
            for e in errs:
                messages.error(request, str(e))
            continue

        file_type = _detect_type(f)

        try:
            cleaned_file = form.cleaned_data["file"]
            # Ensure file pointer is at the beginning
            if hasattr(cleaned_file, 'seek'):
                cleaned_file.seek(0)
            
            logger.info(f"Creating Media object for file: {cleaned_file.name}, type: {file_type}")
            Media.objects.create(
                user=request.user,
                file=cleaned_file,
                file_type=file_type,
                content_type=post_content_type,
                object_id=post.id,
            )
            uploaded_any = True
        except ValidationError as e:
            messages.error(request, f"{f.name}: {e}")
        except Exception:
            logger.warning(
                "Media upload failed for %s",
                getattr(f, "name", "file"),
                exc_info=True,
            )
            messages.error(
                request,
                f"{getattr(f, 'name', 'file')}: upload failed (invalid/unsupported file)."
            )

    return uploaded_any

def get_post_media(post_id):
    post_content_type = ContentType.objects.get_for_model(Post)
    return Media.objects.filter(
        content_type=post_content_type,
        object_id=post_id
    ).order_by('uploaded_at')


def is_image(media):
    return media.is_image


def is_video(media):
    return media.is_video