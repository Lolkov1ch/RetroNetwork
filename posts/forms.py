from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from cloudinary.exceptions import BadRequest
from django.core.exceptions import ValidationError
from PIL import Image as PilImage

from attachments.models import Media


ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/quicktime']


def validate_uploaded_file(file):
    content_type = getattr(file, "content_type", "")

    if content_type.startswith('image/'):
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Unsupported image type.")

        try:
            file.seek(0)
            img = PilImage.open(file)
            img.verify()
            file.seek(0)  
        except Exception:
            raise ValidationError("Invalid image file.")

    elif content_type.startswith('video/'):
        if content_type not in ALLOWED_VIDEO_TYPES:
            raise ValidationError("Unsupported video type.")

    else:
        raise ValidationError("File must be an image or video.")


def handle_media_upload(request, obj):
    files = request.FILES.getlist("images") 

    if not files:
        return

    content_type = ContentType.objects.get_for_model(obj)

    for f in files:
        try:
            validate_uploaded_file(f)

            Media.objects.create(
                user=request.user,
                file=f,
                content_type=content_type,
                object_id=obj.id
            )

        except ValidationError as e:
            messages.error(request, f"{f.name}: {e}")

        except BadRequest:
            messages.error(request, f"{f.name}: Invalid image file.")

        except Exception:
            messages.error(request, f"{f.name}: Upload failed.")