from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError

from attachments.models import Media
from .forms import PostMediaForm
from .thumbnail_utils import generate_post_thumbnail


def handle_media_upload(request, post) -> bool:
    files = request.FILES.getlist("images") # contentReference[oaicite:2]{index=2}

    if not files:
        return True

    if len(files) > settings.MAX_FILES_PER_UPLOAD:  # :contentReference[oaicite:3]{index=3}
        messages.error(request, f"Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed.")
        return False

    uploaded_any = False

    for f in files:
        if f.size > settings.MAX_UPLOAD_SIZE:  # :contentReference[oaicite:4]{index=4}
            messages.error(request, f"{f.name} exceeds maximum file size.")
            continue

        media_form = PostMediaForm(data={}, files={"file": f})

        if not media_form.is_valid():  # :contentReference[oaicite:5]{index=5}
            for error in media_form.errors.get("file", []):
                messages.error(request, str(error))
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
            )  # :contentReference[oaicite:6]{index=6}
            uploaded_any = True

        except ValidationError as e:
            messages.error(request, str(e))

        except Exception as e:
            messages.error(request, f"{f.name}: upload failed ({e.__class__.__name__}).")

    if uploaded_any:
        generate_post_thumbnail(post)  # :contentReference[oaicite:7]{index=7}

    return True