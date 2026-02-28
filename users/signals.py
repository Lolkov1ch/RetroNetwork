from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(user_logged_in)
def set_status_online_on_login(sender, request, user, **kwargs):
    # Defensive: ensure we have a real user instance
    try:
        if not user or getattr(user, 'is_anonymous', False):
            return
    except Exception:
        return

    if getattr(user, 'previous_status', None) and user.previous_status != 'offline':
        user.status = user.previous_status
    else:
        user.status = 'online'
    user.save(update_fields=['status'])


@receiver(user_logged_out)
def set_status_offline_on_logout(sender, request, user, **kwargs):
    try:
        if not user or getattr(user, 'is_anonymous', False):
            return
    except Exception:
        return

    # Preserve previous status only if it isn't already 'offline'
    try:
        if getattr(user, 'status', None) and user.status != 'offline':
            user.previous_status = user.status
    except Exception:
        user.previous_status = 'offline'

    user.status = 'offline'
    user.save(update_fields=['status', 'previous_status'])
