from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from attachments.models import Media
from .models import Post
from .forms import PostMediaForm
from .thumbnail_utils import generate_post_thumbnail

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
VIDEO_EXTENSIONS = (".mp4", ".webm", ".avi", ".mov", ".mkv")


def is_image(media: Media) -> bool:
    return media.file.name.lower().endswith(IMAGE_EXTENSIONS)


def is_video(media: Media) -> bool:
    return media.file.name.lower().endswith(VIDEO_EXTENSIONS)


def get_post_media(post_id: int):
    return Media.objects.filter(
        content_type=ContentType.objects.get_for_model(Post),
        object_id=post_id,
    )


def _human_error_from_exception(exc: Exception) -> str:
    msg = str(exc).strip()

    if not msg:
        msg = exc.__class__.__name__

    return msg


def handle_media_upload(request, post) -> bool:
    files = request.FILES.getlist("images")

    if not files:
        return True

    if len(files) > getattr(settings, "MAX_FILES_PER_UPLOAD", 10):
        messages.error(request, f"Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed.")
        return False

    any_saved = False

    for f in files:
        max_upload = getattr(settings, "MAX_UPLOAD_SIZE", 25 * 1024 * 1024)
        if getattr(f, "size", 0) > max_upload:
            messages.error(request, f"{f.name} exceeds maximum file size.")
            continue

        media_form = PostMediaForm(files={"file": f})
        if not media_form.is_valid():
            for error in media_form.errors.get("file", []):
                messages.error(request, error)
            continue

        try:
            f.seek(0)
        except Exception:
            pass

        try:
            Media.objects.create(
                user=request.user,
                file=f,              
                content_object=post,
            )
            any_saved = True

        except ValidationError as e:
            messages.error(request, f"{f.name}: {e}")

        except Exception as e:
            messages.error(request, f"{f.name}: {_human_error_from_exception(e)}")
            continue

    if any_saved:
        try:
            generate_post_thumbnail(post)
        except Exception:
            pass

    return any_saved