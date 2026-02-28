import logging

from django.contrib import messages
from django.core.exceptions import ValidationError

from attachments.models import Media
from .forms import PostMediaForm

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