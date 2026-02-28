# Production Fix: Message Saving Issue on Render.com

## Problem
The application was throwing `cloudinary.exceptions.BadRequest: Invalid image file` errors when saving messages with images or videos in production on Render.com.

### Root Cause
The issue was in the `Message.save()` method in `messaging/models.py`. The original code:

```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    super().save(*args, **kwargs)  # First save attempt
    
    if is_new:
        if self.message_type == 'image':
            self.generate_image_thumbnail()
            self.save(update_fields=['image_thumbnail'])  # Second save attempt
```

This caused two problems:
1. **Thumbnail Generation After Upload**: The thumbnail was being generated AFTER the initial file upload to Cloudinary, which could result in the thumbnail field being empty or invalid when Django's pre_save hook tried to upload it.
2. **Double Save Overhead**: Multiple save calls meant multiple Cloudinary upload attempts, with some having incomplete data.
3. **File State Issues**: When the first `super().save()` was called, if the image/video file hadn't been properly attached yet, or was in an invalid state, Cloudinary would reject it as an invalid image file.

## Solution

### Changed Approach
The fix reorders the operation to generate thumbnails **before** the initial save:

```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    
    # Generate thumbnails BEFORE saving (so files are ready for Cloudinary)
    if is_new:
        if self.message_type == 'image' and self.image:
            try:
                self.generate_image_thumbnail()
            except Exception as e:
                logger.warning(f"Failed to generate image thumbnail: {e}", exc_info=True)
        elif self.message_type == 'video' and self.video:
            try:
                self.generate_video_thumbnail()
            except Exception as e:
                logger.warning(f"Failed to generate video thumbnail: {e}", exc_info=True)
    
    # Now save with all prepared fields
    super().save(*args, **kwargs)
```

### Benefits
1. **Single Save Call**: Only one call to `super().save()`, reducing Cloudinary uploads
2. **Proper File State**: Thumbnails are generated and ready before the file upload attempt
3. **Better Error Handling**: Thumbnail generation failures are logged but don't crash the save operation
4. **Atomic Operation**: Everything is prepared before the Cloudinary upload happens

### Related Changes
Also removed redundant thumbnail generation code from `messaging/views.py` that was duplicating the logic. The `perform_create()` method now simply sets the file field and calls save() - the thumbnail generation happens automatically in the model's save() method.

## Files Modified
- `messaging/models.py` - Message.save() method refactored
- `messaging/views.py` - Removed duplicate thumbnail generation code

## Testing
The fix ensures:
- Image messages save successfully to Cloudinary
- Video messages save successfully to Cloudinary
- Voice messages with attachments save correctly
- Thumbnail generation doesn't block the main file upload
- Errors in thumbnail generation are logged but don't crash the save

## Deployment
Simply restart the application on Render.com. The fix is backward compatible with existing messages and doesn't require database migrations.
