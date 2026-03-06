from cloudinary_storage.storage import (
    MediaCloudinaryStorage,
    RawMediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


class AvatarCloudinaryStorage(MediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "image"
    
    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class ImageCloudinaryStorage(MediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "image"
    
    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class ChatVideoCloudinaryStorage(VideoMediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "video"
    
    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)


class RawFileCloudinaryStorage(RawMediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "raw"
    
    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        return super()._save(name, content)