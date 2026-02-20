import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

THUMBNAIL_WIDTH = 250
THUMBNAIL_HEIGHT = 200
COLLAGE_WIDTH = 250
COLLAGE_HEIGHT = 200

def get_video_thumbnail(video_path):
    return None


def create_thumbnail(image_file, width=THUMBNAIL_WIDTH, height=THUMBNAIL_HEIGHT):
    try:
        img = Image.open(image_file)
        img = img.convert('RGB')
        
        img_ratio = img.width / img.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None


def create_collage_from_files(media_files, width=COLLAGE_WIDTH, height=COLLAGE_HEIGHT):
    if not media_files:
        return None
    
    image_files = [m for m in media_files if is_image_media(m)]
    
    if not image_files:
        return None
    
    if len(image_files) == 1:
        return create_thumbnail(image_files[0], width, height)
    
    return create_multi_image_collage(image_files, width, height)


def create_multi_image_collage(image_files, width=COLLAGE_WIDTH, height=COLLAGE_HEIGHT):
    try:
        num_images = len(image_files)
        
        if num_images == 2:
            cols, rows = 2, 1
        elif num_images == 3:
            cols, rows = 3, 1
        elif num_images == 4:
            cols, rows = 2, 2
        else:
            cols = 2
            rows = (num_images + cols - 1) // cols
        
        tile_width = width // cols
        tile_height = height // rows
        
        collage = Image.new('RGB', (width, height), (245, 245, 245))
        
        for idx, image_file in enumerate(image_files[:cols * rows]):
            row = idx // cols
            col = idx % cols
            
            img = Image.open(image_file)
            img = img.convert('RGB')
            
            img_ratio = img.width / img.height
            tile_ratio = tile_width / tile_height
            
            if img_ratio > tile_ratio:
                new_width = int(img.height * tile_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                new_height = int(img.width / tile_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))
            
            img = img.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
            
            x = col * tile_width
            y = row * tile_height
            collage.paste(img, (x, y))
        
        return collage
    except Exception as e:
        logger.error(f"Error creating collage: {e}")
        return None


def is_image_media(media_file):
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
    return media_file.name.lower().endswith(IMAGE_EXTENSIONS)


def is_video_media(media_file):
    VIDEO_EXTENSIONS = ('.mp4', '.webm', '.avi', '.mov', '.mkv')
    return media_file.name.lower().endswith(VIDEO_EXTENSIONS)


def save_thumbnail_to_file(pil_image, filename_prefix):
    if pil_image is None:
        return None
    
    try:
        thumbnail_path = os.path.join('thumbnails', filename_prefix + '_thumbnail.jpg')
        thumbnail_path = thumbnail_path.replace('\\', '/')
        thumbnail_full_path = os.path.join(settings.MEDIA_ROOT, thumbnail_path)
        
        os.makedirs(os.path.dirname(thumbnail_full_path), exist_ok=True)
        
        pil_image.save(thumbnail_full_path, 'JPEG', quality=85)

        return thumbnail_path.replace(os.sep, '/')
    except Exception as e:
        logger.error(f"Error saving thumbnail: {e}")
        return None


def generate_post_thumbnail(post):
    from attachments.models import Media
    from posts.models import Post
    from django.contrib.contenttypes.models import ContentType
    
    media_files = Media.objects.filter(
        content_type=ContentType.objects.get_for_model(Post),
        object_id=post.id
    ).order_by('uploaded_at')
    
    if not media_files:
        return None
    
    media_list = [m.file for m in media_files]

    images = [m for m in media_list if is_image_media(m)]
    videos = [m for m in media_list if is_video_media(m)]

    thumbnail_image = None
    
    if images:
        thumbnail_image = create_collage_from_files(images)
    elif videos:
        return None
    
    if thumbnail_image:
        thumbnail_path = save_thumbnail_to_file(thumbnail_image, f"post_{post.id}")
        return thumbnail_path
    
    return None
