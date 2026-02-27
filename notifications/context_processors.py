from notifications.models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:10]
    else:
        notifications = []
    return {'notifications': notifications}
