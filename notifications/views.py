
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .models import Notification

def serialize_notification(n):
    sender_avatar = ''
    sender_name = 'Notification'
    if n.sender:
        sender_name = n.sender.handle or n.sender.username
        try:
            if n.sender.avatar and n.sender.avatar.name:
                sender_avatar = n.sender.avatar.url
        except (AttributeError, FileNotFoundError):
            pass
    
    # Fall back to stored avatar or name
    if not sender_avatar:
        sender_avatar = n.sender_avatar or ''
    if not sender_name or sender_name == 'Notification':
        sender_name = n.sender_name or 'Notification'
    
    return {
        'id': n.id,
        'type': n.get_type_display(),
        'content': n.content,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%b %d, %H:%M'),
        'sender_avatar': sender_avatar,
        'sender_name': sender_name,
    }

@login_required
def notifications_json(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [serialize_notification(n) for n in notifications]
    return JsonResponse({'notifications': data})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.filter(user=request.user, id=notification_id).first()
    if notification:
        notification.is_read = True
        notification.save()
    return JsonResponse({'status': 'ok'})

@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    try:
        count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok', 'success': True, 'updated_count': count})
    except Exception as e:
        print(f"Error marking notifications as read: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)