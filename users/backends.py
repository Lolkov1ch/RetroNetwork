from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            user = None
        
        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
    
        if user is None:
            try:
                user = User.objects.get(handle=username)
            except User.DoesNotExist:
                return None

        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
