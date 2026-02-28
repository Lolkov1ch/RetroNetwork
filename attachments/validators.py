import mimetypes
import os
from django.core.exceptions import ValidationError
from django.conf import settings

ALLOWED_MIME_TYPES = {
    'image': {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml',
    },
    'video': {
        'video/mp4',
        'video/webm',
        'video/quicktime',
        'video/x-msvideo',
        'video/x-matroska',
    },
    'audio': {
        'audio/mpeg',
        'audio/wav',
        'audio/mp4',
        'audio/ogg',
    },
    'document': {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
    }
}

EXTENSION_TO_TYPE = {
    '.jpg': 'image',
    '.jpeg': 'image',
    '.png': 'image',
    '.gif': 'image',
    '.webp': 'image',
    '.svg': 'image',
    '.mp4': 'video',
    '.webm': 'video',
    '.mov': 'video',
    '.avi': 'video',
    '.mkv': 'video',
    '.mp3': 'audio',
    '.wav': 'audio',
    '.m4a': 'audio',
    '.ogg': 'audio',
    '.pdf': 'document',
    '.doc': 'document',
    '.docx': 'document',
    '.txt': 'document',
    '.xlsx': 'document',
    '.xls': 'document',
}

MAX_FILE_SIZES = {
    'image': 25 * 1024 * 1024,  # 25 MB
    'video': 500 * 1024 * 1024,  # 500 MB
    'audio': 100 * 1024 * 1024,  # 100 MB
    'document': 50 * 1024 * 1024,  # 50 MB
}


def validate_file_extension(file):
    if not file:
        return
    
    ext = os.path.splitext(file.name)[1].lower()
    
    if ext not in EXTENSION_TO_TYPE:
        allowed = ', '.join(EXTENSION_TO_TYPE.keys())
        raise ValidationError(
            f'File extension "{ext}" is not allowed. Allowed: {allowed}'
        )


def validate_file_mime_type(file):
    if not file:
        return

    mime_type, _ = mimetypes.guess_type(file.name)
    
    if not mime_type:
        raise ValidationError('Unable to determine file type.')

    allowed_types = []
    for type_list in ALLOWED_MIME_TYPES.values():
        allowed_types.extend(type_list)
    
    if mime_type not in allowed_types:
        raise ValidationError(
            f'File type "{mime_type}" is not allowed. '
            f'Please upload an image, video, audio, or document file.'
        )


def validate_file_size(file):
    if not file:
        return

    ext = os.path.splitext(file.name)[1].lower()
    file_type = EXTENSION_TO_TYPE.get(ext, 'document')

    max_size = MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024)
    
    if file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file.size / (1024 * 1024)
        raise ValidationError(
            f'File size ({actual_mb:.1f}MB) exceeds maximum allowed size '
            f'for {file_type} files ({max_mb:.1f}MB).'
        )


def validate_upload_file(file):
    validate_file_extension(file)
    validate_file_mime_type(file)
    validate_file_size(file)


def get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_TO_TYPE.get(ext, 'unknown')
