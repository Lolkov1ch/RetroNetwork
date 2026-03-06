from cloudinary_storage.storage import (
    MediaCloudinaryStorage,
    RawMediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


class AvatarCloudinaryStorage(MediaCloudinaryStorage):
    """Storage for user avatars - always uses image resource type"""
    def _get_resource_type(self, name):
        return "image"
    
    def _save(self, name, content):
        # Ensure file pointer is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class ImageCloudinaryStorage(MediaCloudinaryStorage):
    """Storage for images in messages and attachments - always uses image resource type"""
    def _get_resource_type(self, name):
        return "image"
    
    def _save(self, name, content):
        # Ensure file pointer is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class ChatVideoCloudinaryStorage(VideoMediaCloudinaryStorage):
    """Storage for videos in messages - always uses video resource type"""
    def _get_resource_type(self, name):
        return "video"
    
    def _save(self, name, content):
        # Ensure file pointer is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class RawFileCloudinaryStorage(RawMediaCloudinaryStorage):
    """Storage for audio, voice messages, and other files - always uses raw resource type"""
    def _get_resource_type(self, name):
        return "raw"
    
    def _save(self, name, content):
        # Ensure file pointer is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)