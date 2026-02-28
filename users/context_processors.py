from .models import User

def status_choices(request):
    return {
        'status_choices': User.STATUS_CHOICES,
    }


def online_friends(request):
    online_friends_list = []
    if request.user.is_authenticated:
        following_ids = request.user.following.values_list('following_id', flat=True)
        if following_ids:
            online_friends_list = User.objects.filter(
                id__in=following_ids,
                status__in=['online', 'dnd', 'inactive']
            ).order_by('display_name')
    
    return {
        'online_friends': online_friends_list,
    }
