from cloudinary_storage.storage import (
    MediaCloudinaryStorage,
    RawMediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


class AvatarCloudinaryStorage(MediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "image"


class ImageCloudinaryStorage(MediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "image"


class ChatVideoCloudinaryStorage(VideoMediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "video"


class RawFileCloudinaryStorage(RawMediaCloudinaryStorage):
    def _get_resource_type(self, name):
        return "raw"