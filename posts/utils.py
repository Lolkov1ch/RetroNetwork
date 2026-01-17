from django.conf import settings
from django.contrib import messages
from .models import Post
from attachments.models import Media
from .forms import PostMediaForm
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.ogg', '.avi', '.mov', '.wmv', '.flv', '.mkv')

def is_image(media):
    return media.file.name.lower().endswith(IMAGE_EXTENSIONS)

def is_video(media):
    return media.file.name.lower().endswith(VIDEO_EXTENSIONS)

def get_post_media(post_id):
    return Media.objects.filter(
        content_type=ContentType.objects.get_for_model(Post),
        object_id=post_id
    )

def handle_media_upload(request, post):
    files = request.FILES.getlist("images")
    
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        messages.error(request, f"Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed.")
        return False
    
    for f in files:
        if f.size > settings.MAX_UPLOAD_SIZE:
            messages.error(request, f"{f.name} exceeds maximum file size.")
            continue

        media_form = PostMediaForm(files={'file': f})
        if not media_form.is_valid():
            for error in media_form.errors.get('file', []):
                messages.error(request, error)
            continue
            
        try:
            Media.objects.create(
                user=request.user,
                file=f,
                content_object=post
            )
        except ValidationError as e:
            messages.error(request, str(e))
    
    return True