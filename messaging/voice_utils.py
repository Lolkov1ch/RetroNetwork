"""
Utility functions for voice message handling with attachments.

This module provides helper functions for creating, validating, and processing
voice messages with photo/video attachments.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import Message, MessageAttachment


def validate_attachment_file(file, attachment_type):
    """
    Validate a single attachment file before upload.
    
    Args:
        file: Django UploadedFile object
        attachment_type: 'image' or 'video'
        
    Returns:
        True if valid
        
    Raises:
        DRFValidationError: If validation fails
    """
    from .views import _validate_uploaded_file, _rewind
    
    try:
        _validate_uploaded_file(file, kind=attachment_type)
        _rewind(file)
        return True
    except DRFValidationError as e:
        raise e


def create_voice_message_with_attachments(message, attachment_files, attachment_types):
    """
    Create a voice message and attach multiple photos/videos to it.
    
    This is a transactional operation - if any attachment fails to upload,
    the entire operation rolls back.
    
    Args:
        message: Message instance (must already be saved)
        attachment_files: List of file objects
        attachment_types: List of attachment types ('image' or 'video')
        
    Returns:
        List of created MessageAttachment instances
        
    Raises:
        DRFValidationError: If any attachment fails validation or upload
    """
    
    if not attachment_files or not attachment_types:
        return []
    
    created_attachments = []
    
    try:
        with transaction.atomic():
            for idx, attachment_file in enumerate(attachment_files):
                if idx >= len(attachment_types):
                    break
                    
                att_type = attachment_types[idx]
                
                if att_type not in {'image', 'video'}:
                    raise DRFValidationError({
                        'attachments': f'Invalid attachment type: {att_type}'
                    })
                
                # Validate the file
                validate_attachment_file(attachment_file, att_type)
                
                # Create the attachment
                attachment = MessageAttachment.objects.create(
                    message=message,
                    attachment_type=att_type,
                    file=attachment_file
                )
                
                created_attachments.append(attachment)
                
    except DRFValidationError:
        raise
    except Exception as e:
        raise DRFValidationError({
            'attachments': f'Failed to create attachments: {str(e)}'
        })
    
    return created_attachments


def get_message_attachments_summary(message):
    """
    Get a summary of attachments for a message.
    
    Args:
        message: Message instance
        
    Returns:
        dict with attachment counts and types
    """
    attachments = message.attachments.all()
    
    summary = {
        'total': attachments.count(),
        'images': attachments.filter(attachment_type='image').count(),
        'videos': attachments.filter(attachment_type='video').count(),
        'attachments': list(attachments.values(
            'id', 'attachment_type', 'file', 'thumbnail', 'created_at'
        ))
    }
    
    return summary


def get_voice_messages_with_attachments(conversation):
    """
    Get all voice messages in a conversation that have attachments.
    
    Args:
        conversation: Conversation instance
        
    Returns:
        QuerySet of Message instances with attachments prefetched
    """
    return (
        conversation.messages
        .filter(message_type='voice')
        .prefetch_related('attachments')
        .filter(attachments__isnull=False)
        .distinct()
    )


def calculate_attachment_storage_usage(user):
    """
    Calculate total storage usage for a user's message attachments.
    
    Args:
        user: User instance
        
    Returns:
        dict with storage information in bytes and MB
    """
    from django.db.models import Sum
    
    # Get total size of attachment files
    attachments = MessageAttachment.objects.filter(message__sender=user)
    
    total_bytes = 0
    for attachment in attachments:
        if attachment.file:
            total_bytes += attachment.file.size
    
    total_mb = round(total_bytes / (1024 * 1024), 2)
    
    return {
        'total_bytes': total_bytes,
        'total_mb': total_mb,
        'attachment_count': attachments.count(),
        'image_count': attachments.filter(attachment_type='image').count(),
        'video_count': attachments.filter(attachment_type='video').count(),
    }


def delete_message_with_attachments(message):
    """
    Delete a message and all its attachments.
    
    Cascading delete is handled by Django, but this function
    provides a transaction-wrapped convenience method.
    
    Args:
        message: Message instance
        
    Returns:
        Number of objects deleted
    """
    try:
        with transaction.atomic():
            # Get attachment count before deletion
            attachment_count = message.attachments.count()
            
            # Delete message (cascades to attachments)
            message.delete()
            
            return attachment_count + 1  # +1 for the message itself
    except Exception as e:
        raise ValidationError(f'Failed to delete message: {str(e)}')
