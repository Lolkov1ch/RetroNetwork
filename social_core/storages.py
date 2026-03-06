import mimetypes

class SmartCloudinaryStorage:
    
    def __new__(cls, **settings):
        from cloudinary_storage.storage import MediaCloudinaryStorage
        
        class SmartMediaCloudinaryStorage(MediaCloudinaryStorage):
            def _get_resource_type(self, name=None, content=None):
                if content and hasattr(content, 'content_type') and content.content_type:
                    content_type = content.content_type
                    if content_type.startswith('image/'):
                        return 'image'
                    elif content_type.startswith('video/'):
                        return 'video'
                    else:
                        return 'raw'

                if name:
                    content_type, _ = mimetypes.guess_type(name)
                    if content_type:
                        if content_type.startswith('image/'):
                            return 'image'
                        elif content_type.startswith('video/'):
                            return 'video'
                        else:
                            return 'raw'

                    name_lower = name.lower()
                    if any(name_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']):
                        return 'image'
                    elif any(name_lower.endswith(ext) for ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']):
                        return 'video'
                    elif any(name_lower.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.ogg', '.aac', '.flac']):
                        return 'raw'
                
                return 'raw'
        
        return SmartMediaCloudinaryStorage(**settings)